#!/usr/bin/env python3
import os
import re
import paramiko
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress_bar import ProgressBar
import time
import getpass
from datetime import datetime

# Initialize rich console
console = Console()

def read_zshrc_aliases():
    """Read server aliases from .zshrc file"""
    zshrc_path = os.path.expanduser("~/.zshrc")
    server_info = []
    
    try:
        with open(zshrc_path, 'r') as f:
            content = f.read()
            # Find all ssh commands
            ssh_pattern = r'ssh -P (\d+) (\w+)@([\d\.]+)'
            matches = re.finditer(ssh_pattern, content)
            
            for match in matches:
                port, username, host = match.groups()
                server_info.append({
                    'host': host,
                    'username': username,
                    'port': int(port)
                })
    except FileNotFoundError:
        console.print("[red]Error: .zshrc file not found[/red]")
        return []
    
    return server_info

def parse_gpu_info(gpu_info):
    """Parse GPU information into a structured format"""
    gpus = []
    lines = gpu_info.strip().split('\n')
    
    # Skip header lines (first 2 lines)
    for line in lines[2:]:
        if not line.strip():
            continue
            
        parts = line.split()
        if len(parts) >= 13:  # nvidia-smi output has at least 13 columns
            gpu = {
                'id': parts[1],
                'name': parts[2],
                'memory_used': parts[8],
                'memory_total': parts[10],
                'utilization': parts[12]
            }
            gpus.append(gpu)
    
    return gpus

def parse_storage_info(storage_info):
    """Parse storage information into a structured format"""
    storage = []
    lines = storage_info.strip().split('\n')
    
    # Skip header line
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 6:
            storage.append({
                'filesystem': parts[0],
                'size': parts[1],
                'used': parts[2],
                'available': parts[3],
                'use_percent': parts[4],
                'mounted_on': parts[5]
            })
    
    return storage

def get_server_info(server, password):
    """Get GPU and storage information from a server"""
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to server
        ssh.connect(
            server['host'],
            port=server['port'],
            username=server['username'],
            password=password
        )
        
        # Get GPU information
        gpu_info = ""
        try:
            _, stdout, _ = ssh.exec_command('nvidia-smi')
            gpu_info = stdout.read().decode()
        except:
            gpu_info = "No GPU information available"
        
        # Get storage information
        _, stdout, _ = ssh.exec_command('df -h')
        storage_info = stdout.read().decode()
        
        ssh.close()
        
        return {
            'gpu_info': parse_gpu_info(gpu_info),
            'storage_info': parse_storage_info(storage_info)
        }
    except Exception as e:
        return {
            'error': str(e)
        }

def create_gpu_table(gpus):
    """Create a formatted table for GPU information"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("GPU ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Memory Used", style="yellow")
    table.add_column("Memory Total", style="yellow")
    table.add_column("Utilization", style="blue")
    
    for gpu in gpus:
        table.add_row(
            gpu['id'],
            gpu['name'],
            gpu['memory_used'],
            gpu['memory_total'],
            gpu['utilization']
        )
    
    return table

def create_storage_table(storage):
    """Create a formatted table for storage information"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Filesystem", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Used", style="yellow")
    table.add_column("Available", style="yellow")
    table.add_column("Use%", style="blue")
    table.add_column("Mounted on", style="green")
    
    for disk in storage:
        use_percent = int(disk['use_percent'].rstrip('%'))
        style = "red" if use_percent > 90 else "yellow" if use_percent > 70 else "green"
        
        table.add_row(
            disk['filesystem'],
            disk['size'],
            disk['used'],
            disk['available'],
            f"[{style}]{disk['use_percent']}[/{style}]",
            disk['mounted_on']
        )
    
    return table

def display_server_info(server, info):
    """Display server information in a formatted way"""
    console.print(Panel(f"[bold blue]Server: {server['host']}[/bold blue]"))
    
    if 'error' in info:
        console.print(f"[red]Error: {info['error']}[/red]")
        return
    
    # Display GPU information
    console.print("\n[bold green]GPU Information:[/bold green]")
    if info['gpu_info']:
        console.print(create_gpu_table(info['gpu_info']))
    else:
        console.print("[yellow]No GPU information available[/yellow]")
    
    # Display storage information
    console.print("\n[bold green]Storage Information:[/bold green]")
    console.print(create_storage_table(info['storage_info']))
    console.print("\n" + "="*80 + "\n")

def main():
    # Read server information
    servers = read_zshrc_aliases()
    
    if not servers:
        console.print("[red]No servers found in .zshrc file[/red]")
        return
    
    # Get password from user
    password = getpass.getpass("Enter server password: ")
    
    while True:
        console.clear()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        console.print(Panel(f"[bold yellow]Server Monitoring Dashboard[/bold yellow]\n[dim]Last updated: {current_time}[/dim]"))
        console.print(f"Monitoring {len(servers)} servers...\n")
        
        for server in servers:
            info = get_server_info(server, password)
            display_server_info(server, info)
        
        # time.sleep(60)
        break

if __name__ == "__main__":
    main()