#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import subprocess

class CompileCommandsGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.compile_commands = []
        self._cached_include_paths = None
        
        # ==================== USER CONFIGURATION AREA ====================
        # Add source folders to search for source files (relative to project root)
        # Script will automatically add all subdirectories to include search paths
        self.source_search_folders = [
            # FreeRTOS source directories
            "FreeRTOS/Source",
            
            # STM32F407 project source directories
            "zproject/Stm32F407_FreeRTOS_Project/ALIENTEK_Explorer_F407ZGT6",
            "zproject/Stm32F407_FreeRTOS_Project/Msp_Common_hal",
        ]
        
        # Add include search folders that should be added to header search paths
        # Script will automatically include these paths and all their subdirectories
        self.include_search_folders = [
            # Standard FreeRTOS header paths
            "FreeRTOS/Source/include",
            
            # Project-specific header paths
            "zproject/Stm32F407_FreeRTOS_Project/ALIENTEK_Explorer_F407ZGT6/HAL",
            "zproject/Stm32F407_FreeRTOS_Project/Msp_Common_hal/APL",
            "zproject/Stm32F407_FreeRTOS_Project/Msp_Common_hal/DRV",
            
            # lvgl library header paths
            "zproject/Stm32F407_FreeRTOS_Project/Msp_Common_hal/PKG/lvgl_v9.4",
            "zproject/Stm32F407_FreeRTOS_Project/Msp_Common_hal/PKG/lvgl_v9.4/src",
            
            # Add your own header search paths here:
            # "my_project/include",
            # "third_party/library/include",
            # "external/sdk/headers",
        ]
        
        # Add your custom macro definitions
        self.custom_definitions = [
            "CONFIG_APP_VERSION=\"v2.0.0\"",
            "USE_HAL_DRIVER",
            "STM32F407xx",
            # Add your own macro definitions here:
            # "MY_CUSTOM_DEFINE",
            # "ENABLE_DEBUG",
        ]
        
        # STM32F407 compiler options
        self.compiler_flags = [
            "-mcpu=cortex-m4",
            "-mthumb",
            "-mfloat-abi=soft",
            "-Wall",
            "-Wextra",
            "-std=c99",
            "-fdata-sections",
            "-ffunction-sections",
        ]
        
        # Directory patterns to exclude
        self.exclude_patterns = [
            ".git", "__pycache__", "build", "Debug", "Release", ".vscode", 
            ".cproject", ".project", ".ewp", ".ewd", ".eww",
            "Drivers/CMSIS/Device/ST/STM32F4xx/Source",
            "Middlewares", "Documentation", "Templates", "EWARM", "MDK-ARM"
        ]
        
        # Source file extensions
        self.source_extensions = ['.c', '.cpp', '.cc', '.cxx']
        # ==================== CONFIGURATION AREA END ====================

    def get_all_include_paths(self) -> List[str]:
        """Get all header search paths including subdirectories"""
        if self._cached_include_paths is not None:
            return self._cached_include_paths
            
        include_paths = []
        
        # Add user-specified include search folders and all their subdirectories
        for folder in self.include_search_folders:
            folder_path = self.project_root / folder
            if folder_path.exists():
                include_paths.append(str(folder_path))
                # Recursively add all subdirectories (limit depth to avoid too many paths)
                subdir_count = 0
                for subdir in folder_path.rglob("*"):
                    if subdir.is_dir():
                        include_paths.append(str(subdir))
                        subdir_count += 1
                        # Limit the number of subdirectories to avoid excessive paths
                        if subdir_count > 500:  # Reasonable limit
                            break
                print(f"Added include path: {folder} (with ~{subdir_count} subdirectories)")
            else:
                print(f"Warning: Include path not found: {folder}")
        
        # Add project root directory
        include_paths.append(str(self.project_root))
        
        # Remove duplicates
        self._cached_include_paths = list(set(include_paths))
        return self._cached_include_paths

    def find_source_files(self) -> List[Path]:
        """Find all source files in specified search folders"""
        source_files = []
        
        for search_folder in self.source_search_folders:
            folder_path = self.project_root / search_folder
            if folder_path.exists():
                print(f"Scanning source folder: {search_folder}")
                
                # Recursively find all source files
                for file_path in folder_path.rglob("*"):
                    # Check if it's an excluded directory
                    if any(pattern in str(file_path) for pattern in self.exclude_patterns):
                        continue
                    
                    # Check if it's a source file
                    if file_path.suffix.lower() in self.source_extensions:
                        source_files.append(file_path)
                        
                print(f"   Found source files in {search_folder}")
            else:
                print(f"Warning: Source search folder not found: {search_folder}")
        
        print(f"Total source files found: {len(source_files)}")
        return source_files

    def get_compile_command(self, source_file: Path) -> Dict[str, Any]:
        """Generate compile command for a source file"""
        
        # Determine compiler
        compiler = "arm-none-eabi-gcc"
        if source_file.suffix.lower() in ['.cpp', '.cc', '.cxx']:
            compiler = "arm-none-eabi-g++"
        
        # Build compile command
        command_parts = [compiler, "-c"]
        
        # Add compiler flags
        command_parts.extend(self.compiler_flags)
        
        # Add all header search paths
        all_include_paths = self.get_all_include_paths()
        for include_path in all_include_paths:
            command_parts.extend(["-I", include_path])
        
        # Add macro definitions
        definitions = self.get_definitions_for_file(source_file)
        for definition in definitions:
            command_parts.extend(["-D", definition])
        
        # Add source file
        command_parts.append(str(source_file))
        
        return {
            "directory": str(self.project_root),
            "command": " ".join(command_parts),
            "file": str(source_file)
        }

    def get_definitions_for_file(self, source_file: Path) -> List[str]:
        """Get macro definitions for a specific source file"""
        definitions = set(self.custom_definitions)
        
        # Add specific definitions based on file path
        file_str = str(source_file)
        
        if "FreeRTOS" in file_str:
            definitions.update([
                "FREERTOS",
                "configUSE_PREEMPTION",
                "configUSE_TICKLESS_IDLE",
                "configUSE_IDLE_HOOK",
                "configUSE_TICK_HOOK"
            ])
        
        if "ALIENTEK" in file_str:
            definitions.add("ALIENTEK_EXPLORER")
        
        if "MSP_Common" in file_str or "Msp_Common" in file_str:
            definitions.add("MSP_COMMON_HAL")
        
        if "HAL" in file_str:
            definitions.add("USE_HAL_DRIVER")
        
        # STM32F407 specific definitions
        definitions.update([
            "STM32F407xx",
            "USE_HAL_DRIVER"
        ])
        
        return list(definitions)

    def generate_commands(self):
        """Generate compile commands for all source files"""
        print("\n" + "="*60)
        print("Starting to generate compile_commands.json...")
        print("="*60)
        
        # Find all source files
        source_files = self.find_source_files()
        
        if not source_files:
            print("No source files found!")
            return
        
        print(f"\nGenerating compile commands for {len(source_files)} source files...")
        
        # Generate compile command for each source file
        for i, source_file in enumerate(source_files, 1):
            if i % 100 == 0:
                print(f"   Processed {i} files...")
            
            try:
                command = self.get_compile_command(source_file)
                self.compile_commands.append(command)
            except Exception as e:
                print(f"Error processing file {source_file}: {e}")
        
        print(f"Successfully generated {len(self.compile_commands)} compile commands")

    def save_to_file(self, output_file: str = "compile_commands.json"):
        """Save compile commands to JSON file"""
        output_path = self.project_root / output_file
        
        print(f"\nSaving to file: {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.compile_commands, f, indent=2, ensure_ascii=False)
            
            print(f"compile_commands.json generated: {output_path}")
            print(f"File contains {len(self.compile_commands)} compile commands")
            
            # Show file size
            file_size = output_path.stat().st_size
            print(f"File size: {file_size:,} bytes")
            
        except Exception as e:
            print(f"Error saving file: {e}")

    def show_configuration(self):
        """Display current configuration information"""
        print("\n" + "="*60)
        print("Current Configuration")
        print("="*60)
        
        print(f"Project root directory: {self.project_root}")
        
        print(f"\nSource search folders ({len(self.source_search_folders)}):")
        for i, folder in enumerate(self.source_search_folders, 1):
            folder_path = self.project_root / folder
            status = "EXISTS" if folder_path.exists() else "MISSING"
            print(f"  {i}. [{status}] {folder}")
        
        print(f"\nInclude search folders ({len(self.include_search_folders)}):")
        for i, folder in enumerate(self.include_search_folders, 1):
            folder_path = self.project_root / folder
            status = "EXISTS" if folder_path.exists() else "MISSING"
            print(f"  {i}. [{status}] {folder}")
        
        print(f"\nCompiler flags ({len(self.compiler_flags)}):")
        for i, flag in enumerate(self.compiler_flags, 1):
            print(f"  {i}. {flag}")
        
        print(f"\nMacro definitions ({len(self.custom_definitions)}):")
        for i, definition in enumerate(self.custom_definitions, 1):
            print(f"  {i}. {definition}")
        
        print(f"\nExclude patterns ({len(self.exclude_patterns)}):")
        for i, pattern in enumerate(self.exclude_patterns, 1):
            print(f"  {i}. {pattern}")
        
        print(f"\nSource file extensions: {', '.join(self.source_extensions)}")
        
        print("\n" + "="*60)
        print("To modify configuration, edit the corresponding variables in the script")
        print("="*60)

    def validate_project_structure(self) -> bool:
        """Validate project structure"""
        print("\nValidating project structure...")
        
        issues = []
        
        # Check project root directory
        if not self.project_root.exists():
            issues.append(f"Project root directory does not exist: {self.project_root}")
        
        # Check each source search folder
        for folder in self.source_search_folders:
            folder_path = self.project_root / folder
            if not folder_path.exists():
                issues.append(f"Source search folder does not exist: {folder}")
        
        # Check each include search path
        for folder in self.include_search_folders:
            folder_path = self.project_root / folder
            if not folder_path.exists():
                issues.append(f"Include search path does not exist: {folder}")
        
        if issues:
            print("Project structure validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("Project structure validation passed")
            return True

def main():
    parser = argparse.ArgumentParser(
        description="Generate compile_commands.json file for clangd code completion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_compile_commands.py                    # Generate with default config
  python generate_compile_commands.py --show-config     # Show current configuration
  python generate_compile_commands.py --validate        # Validate project structure
  python generate_compile_commands.py --output my_commands.json  # Specify output file
  python generate_compile_commands.py --verbose         # Verbose output
        """
    )
    
    parser.add_argument(
        "--project-root", 
        default=".", 
        help="Project root directory path (default: current directory)"
    )
    parser.add_argument(
        "--output", 
        default="compile_commands.json", 
        help="Output filename (default: compile_commands.json)"
    )
    parser.add_argument(
        "--show-config", 
        action="store_true", 
        help="Show current configuration information"
    )
    parser.add_argument(
        "--validate", 
        action="store_true", 
        help="Validate project structure"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Resolve project root directory
    project_root = Path(args.project_root).resolve()
    
    print("compile_commands.json Generator")
    print("="*60)
    print(f"Project root directory: {project_root}")
    
    # Check if project root directory exists
    if not project_root.exists():
        print(f"Error: Project root directory does not exist: {project_root}")
        return 1
    
    # Create generator instance
    generator = CompileCommandsGenerator(project_root)
    
    # Show configuration
    if args.show_config:
        generator.show_configuration()
        return 0
    
    # Validate project structure
    if args.validate:
        if generator.validate_project_structure():
            print("Project structure validation passed, safe to generate compile_commands.json")
        else:
            print("Project structure validation failed, please check configuration")
        return 0
    
    # Generate compile commands
    generator.generate_commands()
    
    if not generator.compile_commands:
        print("No compile commands generated")
        return 1
    
    # Save to file
    generator.save_to_file(args.output)
    
    # Show examples
    if args.verbose and generator.compile_commands:
        print(f"\nFirst 3 compile command examples:")
        print("-" * 60)
        for i, cmd in enumerate(generator.compile_commands[:3], 1):
            print(f"{i}. File: {Path(cmd['file']).name}")
            print(f"   Directory: {Path(cmd['directory']).name}")
            print(f"   Command: {cmd['command'][:100]}...")
            print()
    
    print("\n" + "="*60)
    print("compile_commands.json generation completed!")
    print("You can now install clangd plugin in VSCode and use this file for code completion")
    print("Tip: To modify search paths or macro definitions, edit the configuration area at the top of the script")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    exit(main())