import os
from typing import List, Optional

from agents import function_tool
from pydantic import BaseModel

from geai.tools import workspace_tools


class FindFileResult(BaseModel):
    """Represents a single file found by the find_file tool"""
    path: str
    file_type: str  # 'f' for file, 'd' for directory, 'l' for link, 'x' for executable


class FindFileListResult(BaseModel):
    """Result of a find_file operation"""
    files: List[FindFileResult]
    success: bool
    error_message: Optional[str] = None


def find_file_impl(starting_folder: str, filename_pattern: str, file_type: str) -> FindFileListResult:
    """
    Internal implementation of find_file - searches for files within the workspace directory.
    
    This function is used by the find_file tool and can be tested independently.
    
    :param starting_folder: The folder to start searching from
    :param filename_pattern: The pattern to match filenames (supports * and ? wildcards)
    :param file_type: The type of file to find ('f' for file, 'd' for directory, 'l' for link, 'x' for executable)
    :return: FindFileListResult containing found files or error information
    """
    try:
        # Validate file_type parameter
        valid_file_types = {'f', 'd', 'l', 'x'}
        if file_type not in valid_file_types:
            return FindFileListResult(
                files=[],
                success=False,
                error_message=f"Invalid file_type '{file_type}'. Must be one of: {', '.join(sorted(valid_file_types))}"
            )
        
        # Get the full path of the starting folder
        full_starting_path = os.path.abspath(starting_folder)
        
        # Check if starting folder exists
        if not os.path.exists(full_starting_path):
            return FindFileListResult(
                files=[],
                success=False,
                error_message=f"Starting folder does not exist: {full_starting_path}"
            )
        
        # Check if starting folder is a directory
        if not os.path.isdir(full_starting_path):
            return FindFileListResult(
                files=[],
                success=False,
                error_message=f"Starting path is not a directory: {full_starting_path}"
            )
        
        # Convert pattern to regex for matching
        # Escape special regex characters, then convert * to .*, ? to .
        regex_pattern = filename_pattern.replace('.', r'\.')
        regex_pattern = regex_pattern.replace('*', '.*')
        regex_pattern = regex_pattern.replace('?', '.')
        
        import re
        pattern = re.compile(regex_pattern)
        
        found_files = []
        
        # Walk through the directory tree
        for root, dirs, files in os.walk(full_starting_path):
            # Check directories
            if file_type == 'd':
                for dir_name in dirs:
                    full_path = os.path.join(root, dir_name)
                    # Compute relative path from starting folder
                    relative_path = os.path.relpath(full_path, full_starting_path)
                    found_files.append(FindFileResult(
                        path=relative_path,
                        file_type='d'
                    ))
            
            # Check files
            if file_type in ('f', 'x'):
                for file_name in files:
                    full_path = os.path.join(root, file_name)
                    
                    # Check if filename matches the pattern
                    if pattern.match(file_name):
                        # For executable files, check if the file is executable
                        if file_type == 'x':
                            if not os.access(full_path, os.X_OK):
                                continue
                        
                        # Compute relative path from starting folder
                        relative_path = os.path.relpath(full_path, full_starting_path)
                        found_files.append(FindFileResult(
                            path=relative_path,
                            file_type=file_type
                        ))
            
            # Check symlinks
            if file_type == 'l':
                # os.walk doesn't follow symlinks by default, so we need to check manually
                for item in os.listdir(root):
                    item_path = os.path.join(root, item)
                    if os.path.islink(item_path):
                        # Check if filename matches the pattern
                        if pattern.match(item):
                            relative_path = os.path.relpath(item_path, full_starting_path)
                            found_files.append(FindFileResult(
                                path=relative_path,
                                file_type='l'
                            ))
        
        return FindFileListResult(
            files=found_files,
            success=True
        )
        
    except Exception as e:
        return FindFileListResult(
            files=[],
            success=False,
            error_message=f"Error during find_file: {str(e)}"
        )


@function_tool
def find_file(starting_folder: str, filename_pattern: str, file_type: str) -> FindFileListResult:
    """
    Searches for files within the workspace directory.
    
    :param starting_folder: The folder to start searching from
    :param filename_pattern: The pattern to match filenames (supports * and ? wildcards)
    :param file_type: The type of file to find ('f' for file, 'd' for directory, 'l' for link, 'x' for executable)
    :return: FindFileListResult containing found files or error information
    """
    return find_file_impl(starting_folder, filename_pattern, file_type)