"""Beautiful live dashboard for Mimir"""
import time
import psutil
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich import box
from datetime import datetime
import os

console = Console()

class MimirDashboard:
    """Real-time beautiful system dashboard"""
    
    def __init__(self):
        self.start_time = time.time()
        self.cpu_history = []
        self.memory_history = []
        self.update_count = 0
        
    def create_sparkline(self, data, height=3):
        if not data:
            return ""
        max_val = max(data) if max(data) > 0 else 1
        min_val = min(data)
        range_val = max_val - min_val if max_val > min_val else 1
        chars = ['⣀', '⣤', '⣶', '⣿']
        sparkline = []
        for i in range(len(data)):
            val = data[i]
            normalized = int(((val - min_val) / range_val) * (len(chars) - 1))
            sparkline.append(chars[normalized])
        lines = []
        for line in range(height):
            lines.append(''.join(sparkline))
        return '\n'.join(lines)
    
    def create_layout(self):
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        layout["left"].split(
            Layout(name="cpu"),
            Layout(name="memory"),
            Layout(name="disk"),
        )
        layout["right"].split(
            Layout(name="processes"),
            Layout(name="network"),
            Layout(name="predictions"),
        )
        return layout
    
    def get_header(self):
        text = Text()
        text.append("🤖 MIMIR ", style="bold cyan")
        text.append("Intelligent System Dashboard", style="white")
        text.append(f"  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        text.append(f"  |  Uptime: {self.get_uptime()}", style="green")
        return Panel(text, style="bold")
    
    def get_uptime(self):
        uptime_seconds = time.time() - psutil.boot_time()
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        else:
            return f"{hours}h {minutes}m"
    
    def get_cpu_panel(self):
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_percent_per_core = psutil.cpu_percent(interval=0.5, percpu=True)
        
        self.cpu_history.append(cpu_percent)
        if len(self.cpu_history) > 50:
            self.cpu_history.pop(0)
        
        content = Text()
        bar_length = 20
        filled = int(cpu_percent / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        color = "green" if cpu_percent < 70 else "yellow" if cpu_percent < 90 else "red"
        content.append(f"CPU Total: [{color}]{bar}[/{color}] {cpu_percent:.1f}%\n\n")
        
        content.append("Per Core:\n", style="bold")
        for i, core in enumerate(cpu_percent_per_core[:8]):
            core_bar_length = int(core / 10)
            core_bar = "█" * core_bar_length + "░" * (10 - core_bar_length)
            core_color = "green" if core < 70 else "yellow" if core < 90 else "red"
            content.append(f"  Core {i}: [{core_color}]{core_bar}[/{core_color}] {core:3.0f}%\n")
        
        if len(self.cpu_history) > 5:
            content.append(f"\nHistory:\n")
            sparkline = self.create_sparkline(self.cpu_history, height=2)
            content.append(f"{sparkline}\n")
        
        return Panel(content, title="🔥 CPU", border_style="cyan")
    
    def get_memory_panel(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self.memory_history.append(mem.percent)
        if len(self.memory_history) > 50:
            self.memory_history.pop(0)
        
        content = Text()
        bar_length = 30
        filled = int(mem.percent / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        color = "green" if mem.percent < 70 else "yellow" if mem.percent < 90 else "red"
        content.append(f"RAM: [{color}]{bar}[/{color}] {mem.percent:.1f}%\n\n")
        content.append(f"Total:     {mem.total / (1024**3):6.2f} GB\n")
        content.append(f"Available: {mem.available / (1024**3):6.2f} GB\n")
        content.append(f"Used:      {mem.used / (1024**3):6.2f} GB\n")
        content.append(f"Swap:      {swap.used / (1024**3):6.2f}/{swap.total / (1024**3):6.2f} GB ({swap.percent}%)\n")
        
        if len(self.memory_history) > 5:
            content.append(f"\nHistory:\n")
            sparkline = self.create_sparkline(self.memory_history, height=2)
            content.append(f"{sparkline}\n")
        
        return Panel(content, title="💾 Memory", border_style="green")
    
    def get_disk_panel(self):
        content = Text()
        partitions = psutil.disk_partitions()
        
        for part in partitions[:3]:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                bar_length = 20
                filled = int(usage.percent / 100 * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                color = "green" if usage.percent < 70 else "yellow" if usage.percent < 90 else "red"
                content.append(f"{part.mountpoint}:\n")
                content.append(f"[{color}]{bar}[/{color}] {usage.percent:.1f}%\n")
                content.append(f"  Used: {usage.used / (1024**3):.2f} GB\n")
                content.append(f"  Free: {usage.free / (1024**3):.2f} GB\n\n")
            except:
                pass
        
        disk_io = psutil.disk_io_counters()
        if disk_io:
            content.append(f"Disk I/O:\n")
            content.append(f"  Read:  {disk_io.read_bytes / (1024**2):.1f} MB\n")
            content.append(f"  Write: {disk_io.write_bytes / (1024**2):.1f} MB\n")
        
        return Panel(content, title="💽 Disk", border_style="blue")
    
    def get_processes_panel(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 0 or proc.info['memory_percent'] > 0:
                    processes.append(proc.info)
            except:
                pass
        
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        content = Text()
        content.append("🔥 Top by CPU:\n", style="bold")
        for proc in processes[:5]:
            name = proc['name'][:20]
            cpu = proc.get('cpu_percent', 0)
            content.append(f"  {name:20} {cpu:5.1f}%\n")
        
        content.append("\n💾 Top by Memory:\n", style="bold")
        processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        for proc in processes[:5]:
            name = proc['name'][:20]
            mem = proc.get('memory_percent', 0)
            content.append(f"  {name:20} {mem:5.1f}%\n")
        
        content.append(f"\n📊 Total Processes: {len(psutil.pids())}")
        return Panel(content, title="📊 Processes", border_style="magenta")
    
    def get_network_panel(self):
        net_io = psutil.net_io_counters()
        connections = psutil.net_connections()
        
        if hasattr(self, 'last_net_io'):
            sent_rate = (net_io.bytes_sent - self.last_net_io.bytes_sent) / 1024
            recv_rate = (net_io.bytes_recv - self.last_net_io.bytes_recv) / 1024
        else:
            sent_rate = 0
            recv_rate = 0
            self.last_net_io = net_io
        
        content = Text()
        content.append(f"📤 Upload:   {sent_rate:.1f} KB/s\n")
        content.append(f"📥 Download: {recv_rate:.1f} KB/s\n")
        content.append(f"Total Sent: {net_io.bytes_sent / (1024**2):.1f} MB\n")
        content.append(f"Total Recv: {net_io.bytes_recv / (1024**2):.1f} MB\n")
        
        status_count = {}
        for conn in connections[:100]:
            status_count[conn.status] = status_count.get(conn.status, 0) + 1
        
        if status_count:
            content.append(f"\nConnections:\n")
            for status, count in list(status_count.items())[:3]:
                content.append(f"  {status}: {count}\n")
        
        return Panel(content, title="🌐 Network", border_style="yellow")
    
    def get_predictions_panel(self):
        content = Text()
        
        try:
            from core.health.health_score import HealthScore
            health = HealthScore()
            health_score = health.calculate()
            emoji = health.get_emoji()
            content.append(f"{emoji} Health Score: {health_score:.1f}/100\n\n", style="bold")
        except:
            pass
        
        try:
            from core.alerts.alert_manager import AlertManager
            alert_mgr = AlertManager()
            alerts = alert_mgr.check_all()
            if alerts:
                content.append(f"🚨 Active Alerts: {len(alerts)}\n\n")
        except:
            pass
        
        content.append("🔮 Predictions:\n", style="bold cyan")
        
        cpu = psutil.cpu_percent(interval=0.5)
        if cpu > 80:
            hours_to_full = (100 - cpu) / 2
            if hours_to_full < 1:
                content.append("  ⚠️ CPU saturation in < 1 hour\n", style="red")
            elif hours_to_full < 4:
                content.append(f"  ⚠️ CPU saturation in {hours_to_full:.1f} hours\n", style="yellow")
        
        mem = psutil.virtual_memory()
        if mem.percent > 85:
            hours_to_oom = (95 - mem.percent) / 5
            if hours_to_oom < 2:
                content.append("  ⚠️ OOM risk in < 2 hours\n", style="red")
            elif hours_to_oom < 8:
                content.append(f"  ⚠️ OOM risk in {hours_to_oom:.1f} hours\n", style="yellow")
        
        disk = psutil.disk_usage('/')
        if disk.percent > 85:
            days_to_full = (100 - disk.percent) * 7
            content.append(f"  ⚠️ Disk full in ~{days_to_full:.0f} days\n", style="yellow")
        
        uptime_days = (time.time() - psutil.boot_time()) / 86400
        if uptime_days > 30:
            content.append(f"  💡 Reboot recommended (uptime: {uptime_days:.0f} days)\n", style="green")
        
        if mem.percent > 90:
            content.append("  💊 Try: 'heal memory' to free RAM\n", style="cyan")
        if disk.percent > 90:
            content.append("  💊 Try: 'heal disk' to clean space\n", style="cyan")
        
        if len(content._text) < 100:
            content.append("  ✅ No issues predicted\n")
            content.append("  System is stable\n")
        
        return Panel(content, title="🔮 Predictions & Health", border_style="cyan")
    
    def get_footer(self):
        text = Text()
        text.append("Press Ctrl+C to exit | ", style="dim")
        text.append("Commands: ", style="dim")
        text.append("status ", style="green")
        text.append("top ", style="cyan")
        text.append("memory ", style="blue")
        text.append("disk ", style="yellow")
        text.append("health ", style="magenta")
        text.append("alerts ", style="red")
        return Panel(text, style="dim")
    
    def run(self):
        layout = self.create_layout()
        try:
            with Live(layout, refresh_per_second=2, screen=True) as live:
                while True:
                    layout["header"].update(self.get_header())
                    layout["cpu"].update(self.get_cpu_panel())
                    layout["memory"].update(self.get_memory_panel())
                    layout["disk"].update(self.get_disk_panel())
                    layout["processes"].update(self.get_processes_panel())
                    layout["network"].update(self.get_network_panel())
                    layout["predictions"].update(self.get_predictions_panel())
                    layout["footer"].update(self.get_footer())
                    self.update_count += 1
                    time.sleep(0.5)
        except KeyboardInterrupt:
            console.clear()
            console.print("[bold green]Dashboard closed. Back to Mimir CLI![/bold green]")

def main():
    dashboard = MimirDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()

