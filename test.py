import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime
from tqdm import tqdm
import sys
import time
import os
import glob
from bot import ChessBot

class IterativeChessBotAnalyzer:
    def __init__(self, opening_book_path: str = "resources/komodo.bin", session_name: str = None):
        """
        Analyzer that captures results from iterative deepening in a single search per position
        
        Args:
            opening_book_path: Path to the opening book file
            session_name: Name for this analysis session
        """
        self.opening_book_path = opening_book_path
        self.results = []
        self.summary_stats = {}
        
        # Session management
        if session_name is None:
            self.session_name = f"iterative_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            self.session_name = session_name
            
        self.session_dir = f"analysis_sessions/{self.session_name}"
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Create visualize directory
        self.visualize_dir = f"{self.session_dir}/visualize"
        os.makedirs(self.visualize_dir, exist_ok=True)
        
        # Create checkpoints directory for saving intermediate results
        self.checkpoints_dir = f"{self.session_dir}/checkpoints"
        os.makedirs(self.checkpoints_dir, exist_ok=True)
        
        print(f"📁 Session: {self.session_name}")
        print(f"📂 Session directory: {self.session_dir}")
        print(f"📊 Visualizations: {self.visualize_dir}")
        print(f"💾 Checkpoints: {self.checkpoints_dir}")

    def analyze_fen_list_iterative(self, fen_list: List[str], max_depth: int = 9, 
                                  save_visualize_frequency: int = 10) -> pd.DataFrame:
        """
        Analyze FEN positions using single search per position with iterative deepening capture
        
        Args:
            fen_list: List of FEN strings to analyze
            max_depth: Maximum depth to search (default: 9)
            save_visualize_frequency: Save results and create visualization every N positions (default: 10)
            
        Returns:
            DataFrame containing all results
        """
        print(f"🚀 Starting iterative deepening analysis of {len(fen_list)} FEN positions (max depth: {max_depth})")
        print(f"💾 Saving and visualizing every {save_visualize_frequency} positions")
        print("=" * 80)
        
        # Progress tracking
        total_positions = len(fen_list)
        position_pbar = tqdm(fen_list, desc="Analyzing Positions", unit="pos", colour="green")
        
        skipped_opening_book = 0
        processed_positions = 0
        error_positions = 0
        
        for pos_idx, fen in enumerate(position_pbar):
            try:
                # Create bot for this position
                bot = ChessBot(initial_fen=fen, opening_book_path=self.opening_book_path)
                
                # Run single search to max depth - this captures all depth results
                start_time = time.time()
                best_move = bot.get_best_move(max_depth=max_depth, time_ms=30000)  # 30 second timeout
                total_time = time.time() - start_time
                
                # Get depth results from the search
                depth_results = bot.get_depth_results()
                
                # Check if opening book was used
                if depth_results and any(result.get('from_opening_book', False) for result in depth_results.values()):
                    skipped_opening_book += 1
                    position_pbar.set_postfix({
                        'Status': 'Opening Book',
                        'Skipped': skipped_opening_book,
                        'Processed': processed_positions,
                        'Errors': error_positions
                    })
                    continue
                
                processed_positions += 1
                
                # Process results for each depth
                for depth, result in depth_results.items():
                    if depth > max_depth:
                        continue
                        
                    record = {
                        'fen': fen,
                        'position_index': pos_idx,
                        'depth': depth,
                        'best_move': result.get('best_move'),
                        'execution_time': result.get('execution_time', 0),
                        'cumulative_time': result.get('cumulative_time', 0),
                        'eval': result.get('eval'),
                        'from_opening_book': result.get('from_opening_book', False),
                        'completed': result.get('completed', True),
                        'partial_search': result.get('partial_search', False),
                        'nodes_searched': result.get('nodes_searched', 0),
                        'success': result.get('completed', True) and not result.get('error'),
                        'error': result.get('error'),
                        'timestamp': datetime.now().isoformat(),
                        'total_search_time': total_time
                    }
                    self.results.append(record)
                
                # Update progress bar
                depths_completed = len([d for d in depth_results.keys() if d <= max_depth])
                avg_time_per_depth = total_time / depths_completed if depths_completed > 0 else 0
                
                position_pbar.set_postfix({
                    'Depths': f'{depths_completed}/{max_depth}',
                    'Avg/depth': f'{avg_time_per_depth:.3f}s',
                    'Total': f'{total_time:.2f}s',
                    'Processed': processed_positions,
                    'Skipped': skipped_opening_book,
                    'Errors': error_positions
                })
                
                # Save results and create visualization every N positions
                if processed_positions % save_visualize_frequency == 0 and processed_positions > 0:
                    print(f"\n💾 Saving checkpoint and creating visualization after {processed_positions} positions...")
                    self.save_checkpoint(processed_positions)
                    self.create_interim_visualization(processed_positions)
                
            except Exception as e:
                error_positions += 1
                print(f"\n❌ Error processing position {pos_idx}: {e}")
                
                # Add error records for all depths
                for depth in range(1, max_depth + 1):
                    error_record = {
                        'fen': fen,
                        'position_index': pos_idx,
                        'depth': depth,
                        'best_move': None,
                        'execution_time': None,
                        'cumulative_time': None,
                        'eval': None,
                        'from_opening_book': False,
                        'completed': False,
                        'partial_search': False,
                        'nodes_searched': 0,
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'total_search_time': None
                    }
                    self.results.append(error_record)
                
                position_pbar.set_postfix({
                    'Status': 'ERROR',
                    'Processed': processed_positions,
                    'Skipped': skipped_opening_book,
                    'Errors': error_positions
                })
                continue
        
        position_pbar.close()
        
        # Convert to DataFrame
        df = pd.DataFrame(self.results)
        
        # Save final results
        self.save_results(df)
        
        # Calculate statistics
        self._calculate_summary_stats(df)
        
        # Create final visualizations
        print(f"\n📊 Creating final comprehensive visualizations...")
        self.create_comprehensive_visualizations(df)
        
        print("\n" + "=" * 80)
        print("🎉 Iterative deepening analysis completed!")
        print(f"📈 Total positions processed: {processed_positions}")
        print(f"📖 Positions skipped (opening book): {skipped_opening_book}")
        print(f"❌ Positions with errors: {error_positions}")
        print(f"📊 Total depth records: {len(df)}")
        self._print_summary()
        
        return df

    def save_checkpoint(self, positions_processed: int):
        """Save intermediate results as checkpoint"""
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save checkpoint file
        checkpoint_filename = f"{self.checkpoints_dir}/checkpoint_{positions_processed}_positions_{timestamp}.csv"
        df.to_csv(checkpoint_filename, index=False)
        
        # Also save by depth for this checkpoint
        success_df = df[df['success'] == True]
        if not success_df.empty:
            for depth in sorted(success_df['depth'].unique()):
                depth_df = df[df['depth'] == depth]
                depth_checkpoint_filename = f"{self.checkpoints_dir}/checkpoint_{positions_processed}_depth_{depth}_{timestamp}.csv"
                depth_df.to_csv(depth_checkpoint_filename, index=False)
        
        print(f"   💾 Checkpoint saved: {checkpoint_filename}")

    def create_interim_visualization(self, positions_processed: int):
        """Create interim visualization during analysis"""
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        success_df = df[df['success'] == True]
        
        if success_df.empty:
            return
        
        plt.style.use('default')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Average execution time by depth
        avg_times = success_df.groupby('depth')['execution_time'].mean()
        ax1.plot(avg_times.index, avg_times.values, 'o-', linewidth=2, markersize=8)
        ax1.set_title(f'Avg Execution Time by Depth\n(After {positions_processed} positions)')
        ax1.set_xlabel('Depth')
        ax1.set_ylabel('Average Time (seconds)')
        ax1.set_yscale('log')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for x, y in zip(avg_times.index, avg_times.values):
            ax1.text(x, y*1.1, f'{y:.3f}s', ha='center', va='bottom', fontsize=9)
        
        # 2. Success rate by depth
        success_rates = df.groupby('depth')['success'].mean() * 100
        bars = ax2.bar(success_rates.index, success_rates.values, alpha=0.7, color='lightgreen')
        ax2.set_title('Success Rate by Depth')
        ax2.set_xlabel('Depth')
        ax2.set_ylabel('Success Rate (%)')
        ax2.set_ylim(0, 105)
        
        # Add value labels
        for bar, value in zip(bars, success_rates.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 3. Cumulative execution time by depth
        cumulative_times = success_df.groupby('depth')['execution_time'].sum()
        ax3.bar(cumulative_times.index, cumulative_times.values, alpha=0.7, color='lightcoral')
        ax3.set_title('Total Execution Time by Depth')
        ax3.set_xlabel('Depth')
        ax3.set_ylabel('Total Time (seconds)')
        
        # 4. Position count by depth
        position_counts = success_df.groupby('depth').size()
        ax4.bar(position_counts.index, position_counts.values, alpha=0.7, color='skyblue')
        ax4.set_title('Completed Positions by Depth')
        ax4.set_xlabel('Depth')
        ax4.set_ylabel('Number of Positions')
        
        # Add summary text box
        total_time = success_df['execution_time'].sum()
        unique_positions = len(success_df['position_index'].unique())
        avg_time_per_position = success_df.groupby('position_index')['execution_time'].sum().mean()
        
        summary_text = f"""📊 Progress Summary:
✅ Positions: {unique_positions}
⏱️ Total Time: {total_time:.1f}s
📈 Avg/Position: {avg_time_per_position:.2f}s
🎯 Success Rate: {(len(success_df)/len(df)*100):.1f}%"""
        
        plt.figtext(0.02, 0.98, summary_text, fontsize=10, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8),
                   verticalalignment='top')
        
        plt.tight_layout()
        plt.suptitle(f'Progress Analysis - {positions_processed} Positions Processed', 
                    fontsize=14, fontweight='bold', y=0.96)
        
        # Save interim visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        interim_filename = f"{self.visualize_dir}/progress_{positions_processed}_positions_{timestamp}.png"
        plt.savefig(interim_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Progress visualization saved: {interim_filename}")

    def create_depth_specific_visualizations(self, df: pd.DataFrame):
        """Create individual visualizations for each depth"""
        success_df = df[df['success'] == True]
        
        if success_df.empty:
            return
        
        print("   📊 Creating depth-specific visualizations...")
        
        # Get available depths
        available_depths = sorted(success_df['depth'].unique())
        
        for depth in available_depths:
            depth_data = success_df[success_df['depth'] == depth]['execution_time']
            
            if len(depth_data) == 0:
                continue
            
            # Create individual depth visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # 1. Histogram
            ax1.hist(depth_data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            ax1.set_title(f'Execution Time Distribution - Depth {depth}')
            ax1.set_xlabel('Execution Time (seconds)')
            ax1.set_ylabel('Frequency')
            ax1.axvline(depth_data.mean(), color='red', linestyle='--', label=f'Mean: {depth_data.mean():.3f}s')
            ax1.axvline(depth_data.median(), color='green', linestyle='--', label=f'Median: {depth_data.median():.3f}s')
            ax1.legend()
            
            # 2. Box plot
            ax2.boxplot(depth_data, vert=True)
            ax2.set_title(f'Box Plot - Depth {depth}')
            ax2.set_ylabel('Execution Time (seconds)')
            ax2.set_xticklabels([f'Depth {depth}'])
            
            # Add statistics text
            stats_text = f"""
            Count: {len(depth_data)}
            Mean: {depth_data.mean():.3f}s
            Median: {depth_data.median():.3f}s
            Std: {depth_data.std():.3f}s
            Min: {depth_data.min():.3f}s
            Max: {depth_data.max():.3f}s
            """
            ax2.text(1.2, depth_data.max(), stats_text, fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
            
            # 3. Cumulative distribution
            sorted_data = np.sort(depth_data)
            cumulative = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
            ax3.plot(sorted_data, cumulative, marker='o', markersize=3)
            ax3.set_title(f'Cumulative Distribution - Depth {depth}')
            ax3.set_xlabel('Execution Time (seconds)')
            ax3.set_ylabel('Cumulative Probability')
            ax3.grid(True, alpha=0.3)
            
            # 4. Performance percentiles
            percentiles = [10, 25, 50, 75, 90, 95, 99]
            percentile_values = [np.percentile(depth_data, p) for p in percentiles]
            ax4.bar([f'P{p}' for p in percentiles], percentile_values, alpha=0.7, color='lightcoral')
            ax4.set_title(f'Performance Percentiles - Depth {depth}')
            ax4.set_xlabel('Percentile')
            ax4.set_ylabel('Execution Time (seconds)')
            ax4.tick_params(axis='x', rotation=45)
            
            # Add value labels
            for i, (p, v) in enumerate(zip(percentiles, percentile_values)):
                ax4.text(i, v, f'{v:.3f}s', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            plt.suptitle(f'Detailed Analysis - Depth {depth} ({len(depth_data)} positions)', 
                        fontsize=14, fontweight='bold', y=0.98)
            
            # Save depth-specific visualization
            depth_filename = f"{self.visualize_dir}/depth_{depth}_analysis.png"
            plt.savefig(depth_filename, dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"   ✅ Depth-specific visualizations saved for depths: {available_depths}")

    def create_comprehensive_visualizations(self, df: pd.DataFrame):
        """Create comprehensive final visualizations"""
        success_df = df[df['success'] == True]
        
        if success_df.empty:
            print("❌ No successful results for visualization!")
            return
        
        # Create depth-specific visualizations first
        self.create_depth_specific_visualizations(df)
        
        # Create combined analysis
        print("   📊 Creating combined analysis visualizations...")
        
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Summary trends visualization
        fig = plt.figure(figsize=(20, 12))
        
        # Summary table
        plt.subplot(2, 3, 1)
        plt.axis('off')
        
        # Create comprehensive summary table
        depth_stats = success_df.groupby('depth')['execution_time'].agg([
            'count', 'mean', 'median', 'std', 'min', 'max'
        ]).round(4)
        
        table_data = []
        for depth, row in depth_stats.iterrows():
            table_data.append([
                f"Depth {depth}",
                f"{int(row['count'])}",
                f"{row['mean']:.3f}s",
                f"{row['median']:.3f}s",
                f"{row['std']:.3f}s",
                f"{row['min']:.3f}s",
                f"{row['max']:.3f}s"
            ])
        
        table = plt.table(cellText=table_data,
                         colLabels=['Depth', 'Count', 'Mean', 'Median', 'Std', 'Min', 'Max'],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.8)
        
        # Style the table
        for i in range(len(table_data) + 1):
            for j in range(7):
                cell = table[(i, j)]
                if i == 0:  # Header
                    cell.set_facecolor('#4CAF50')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
        
        plt.title('Performance Summary by Depth', fontsize=14, fontweight='bold', pad=20)
        
        # Execution time trends
        plt.subplot(2, 3, 2)
        depth_stats = success_df.groupby('depth')['execution_time'].agg(['mean', 'median', 'std'])
        
        plt.errorbar(depth_stats.index, depth_stats['mean'], yerr=depth_stats['std'], 
                    fmt='o-', linewidth=2, markersize=8, capsize=5, label='Mean ± Std')
        plt.plot(depth_stats.index, depth_stats['median'], 's-', linewidth=2, 
                label='Median', alpha=0.8)
        
        plt.title('Execution Time Trends', fontsize=14, fontweight='bold')
        plt.xlabel('Depth')
        plt.ylabel('Execution Time (seconds)')
        plt.yscale('log')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Success rates
        plt.subplot(2, 3, 3)
        success_rates = df.groupby('depth')['success'].mean() * 100
        colors = ['#4CAF50' if rate > 95 else '#FF9800' if rate > 80 else '#F44336' 
                 for rate in success_rates.values]
        
        bars = plt.bar(success_rates.index, success_rates.values, alpha=0.8, color=colors)
        plt.title('Success Rate by Depth', fontsize=14, fontweight='bold')
        plt.xlabel('Depth')
        plt.ylabel('Success Rate (%)')
        plt.ylim(0, 105)
        
        for bar, value in zip(bars, success_rates.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Performance scaling comparison
        plt.subplot(2, 3, 4)
        avg_times = success_df.groupby('depth')['execution_time'].mean()
        
        # Theoretical scaling models
        if len(avg_times) > 1:
            theoretical_exp = [avg_times.iloc[0] * (2 ** i) for i in range(len(avg_times))]
            theoretical_cubic = [avg_times.iloc[0] * ((i + 1) ** 3) for i in range(len(avg_times))]
            
            plt.plot(avg_times.index, avg_times.values, 'o-', label='Actual', linewidth=3, markersize=10)
            plt.plot(avg_times.index, theoretical_exp, 's--', label='Exponential (2^n)', linewidth=2, alpha=0.7)
            plt.plot(avg_times.index, theoretical_cubic, '^--', label='Cubic (n³)', linewidth=2, alpha=0.7)
            
            plt.title('Performance Scaling Analysis', fontsize=14, fontweight='bold')
            plt.xlabel('Depth')
            plt.ylabel('Execution Time (seconds)')
            plt.yscale('log')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        # Growth rate analysis
        plt.subplot(2, 3, 5)
        if len(avg_times) > 1:
            growth_rates = avg_times.pct_change() * 100
            bars = plt.bar(growth_rates.index[1:], growth_rates.values[1:], alpha=0.7, color='lightcoral')
            plt.title('Growth Rate Between Depths', fontsize=14, fontweight='bold')
            plt.xlabel('Depth')
            plt.ylabel('Growth Rate (%)')
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            plt.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, value in zip(bars, growth_rates.values[1:]):
                if not np.isnan(value):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (5 if value > 0 else -15), 
                            f'{value:.1f}%', ha='center', va='bottom' if value > 0 else 'top', fontsize=9)
        
        # Overall statistics
        plt.subplot(2, 3, 6)
        plt.axis('off')
        
        total_positions = len(df['position_index'].unique())
        total_success = len(success_df)
        total_time = success_df['execution_time'].sum()
        avg_time_per_position = success_df.groupby('position_index')['execution_time'].sum().mean()
        
        if len(avg_times) > 1:
            growth_factor = avg_times.max() / avg_times.min()
            complexity_analysis = f"Growth Factor: {growth_factor:.1f}x"
        else:
            complexity_analysis = "Insufficient data for growth analysis"
        
        summary_text = f"""
📊 ITERATIVE DEEPENING ANALYSIS

🎯 Positions Analyzed: {total_positions:,}
✅ Successful Calculations: {total_success:,}
⏱️  Total Computation Time: {total_time:.2f}s
📈 Depths: {min(success_df['depth'])}-{max(success_df['depth'])}
🕐 Avg Time/Position: {avg_time_per_position:.2f}s

🚀 Performance Insights:
• Fastest Depth: {avg_times.idxmin()} ({avg_times.min():.3f}s avg)
• Slowest Depth: {avg_times.idxmax()} ({avg_times.max():.3f}s avg)
• {complexity_analysis}
• Most Efficient: Depth {avg_times.idxmin()}
• Highest Success: {success_rates.idxmax()}% at depth {success_rates.idxmax()}
"""
        
        plt.text(0.05, 0.95, summary_text, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
                transform=plt.gca().transAxes)
        
        plt.suptitle('🏆 Comprehensive Chess Bot Iterative Deepening Analysis', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        # Save comprehensive visualization
        comprehensive_filename = f"{self.visualize_dir}/comprehensive_analysis.png"
        plt.savefig(comprehensive_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Comprehensive analysis saved: {comprehensive_filename}")

    def save_results(self, df: pd.DataFrame):
        """Save results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save complete results
        complete_filename = f"{self.session_dir}/iterative_analysis_{timestamp}.csv"
        df.to_csv(complete_filename, index=False)
        print(f"💾 Complete results saved: {complete_filename}")
        
        # Save by depth for easy access
        success_df = df[df['success'] == True]
        if not success_df.empty:
            for depth in sorted(success_df['depth'].unique()):
                depth_df = df[df['depth'] == depth]
                depth_filename = f"{self.session_dir}/depth_{depth}_results.csv"
                depth_df.to_csv(depth_filename, index=False)
                print(f"   📊 Depth {depth} results saved: {depth_filename}")

    def _calculate_summary_stats(self, df: pd.DataFrame):
        """Calculate summary statistics"""
        success_df = df[df['success'] == True]
        
        if success_df.empty:
            self.summary_stats = {
                'total_positions': len(df['position_index'].unique()) if not df.empty else 0,
                'total_calculations': 0,
                'total_time': 0,
                'overall_success_rate': 0
            }
            return
        
        # Group by depth
        depth_stats = success_df.groupby('depth')['execution_time'].agg([
            'count', 'mean', 'median', 'std', 'min', 'max', 'sum'
        ]).round(4)
        
        self.summary_stats = {
            'by_depth': depth_stats,
            'total_positions': len(df['position_index'].unique()),
            'total_calculations': len(success_df),
            'total_time': success_df['execution_time'].sum(),
            'overall_success_rate': (len(success_df) / len(df)) * 100
        }

    def _print_summary(self):
        """Print summary statistics"""
        if not self.summary_stats:
            return
        
        print(f"📊 Analysis Summary:")
        print(f"   • Total positions: {self.summary_stats['total_positions']}")
        print(f"   • Total calculations: {self.summary_stats['total_calculations']}")
        print(f"   • Overall success rate: {self.summary_stats['overall_success_rate']:.1f}%")
        print(f"   • Total computation time: {self.summary_stats['total_time']:.2f}s")
        
        if 'by_depth' in self.summary_stats:
            print(f"\n📈 Per-depth Performance:")
            df_stats = self.summary_stats['by_depth']
            print(f"{'Depth':<6} {'Count':<6} {'Mean(s)':<8} {'Median(s)':<9} {'Std(s)':<8} {'Total(s)':<9}")
            print("-" * 60)
            
            for depth, row in df_stats.iterrows():
                print(f"{depth:<6} {int(row['count']):<6} {row['mean']:<8.3f} {row['median']:<9.3f} "
                      f"{row['std']:<8.3f} {row['sum']:<9.2f}")


# Main function for iterative deepening analysis
def run_iterative_deepening_analysis(fen_list: List[str], 
                                    opening_book_path: str = "resources/komodo.bin",
                                    session_name: str = None,
                                    max_depth: int = 9,
                                    save_visualize_frequency: int = 10):
    """
    Run chess analysis using iterative deepening capture - single search per position
    
    Args:
        fen_list: List of FEN positions to analyze
        opening_book_path: Path to opening book
        session_name: Name for this session
        max_depth: Maximum search depth
        save_visualize_frequency: Save and create visualization every N positions (default: 10)
        
    Returns:
        results_df, analyzer
    """
    
    print("🏁 Initializing Iterative Deepening Chess Bot Analyzer...")
    
    # Initialize analyzer
    analyzer = IterativeChessBotAnalyzer(opening_book_path, session_name)
    
    print(f"📋 Analysis Configuration:")
    print(f"   • FEN positions: {len(fen_list)}")
    print(f"   • Max search depth: {max_depth}")
    print(f"   • Opening book: {opening_book_path}")
    print(f"   • Save & visualize frequency: every {save_visualize_frequency} positions")
    print(f"   • Method: Single search per position with depth capture")
    print(f"   • Efficiency: ~{max_depth}x faster than multiple searches")
    
    # Run analysis
    results_df = analyzer.analyze_fen_list_iterative(fen_list, max_depth, save_visualize_frequency)
    
    return results_df, analyzer


# Utility functions
def analyze_single_fen(fen: str, max_depth: int = 9, opening_book_path: str = "resources/komodo.bin"):
    """
    Analyze a single FEN position and return depth results
    
    Args:
        fen: FEN string
        max_depth: Maximum depth to search
        opening_book_path: Path to opening book
        
    Returns:
        dict: Results for each depth
    """
    bot = ChessBot(initial_fen=fen, opening_book_path=opening_book_path)
    
    print(f"🔍 Analyzing position: {fen[:50]}...")
    start_time = time.time()
    best_move = bot.get_best_move(max_depth=max_depth, time_ms=30000)
    total_time = time.time() - start_time
    
    depth_results = bot.get_depth_results()
    
    print(f"✅ Analysis completed in {total_time:.2f}s")
    print(f"📈 Captured {len(depth_results)} depth results")
    print(f"🎯 Best move: {best_move}")
    
    return depth_results


# Example usage
if __name__ == "__main__":
    # Load FEN data
    df_fen = pd.read_csv('resources/train.csv')
    sample_fen_list = df_fen.sample(n=100)['FEN'].to_list()
    
    print("🔥 Iterative Deepening Chess Bot Analysis - Optimized Version")
    print("=" * 80)
    print("🎯 Key Advantages:")
    print("   • ✅ Single search per position (9x more efficient)")
    print("   • 📊 Captures all depths 1-9 in one iterative deepening run")
    print("   • 📖 Automatically skips opening book moves")
    print("   • 🔄 Real-time progress tracking")
    print("   • 💾 Save checkpoints every 10 positions")
    print("   • 📈 Create visualizations every 10 positions")
    print("   • 📊 Individual depth analysis + combined trends")
    
    print(f"\n🚀 Usage Examples:")
    print(f"1. Run full analysis (default: save/visualize every 10 positions):")
    print(f"   results_df, analyzer = run_iterative_deepening_analysis(fen_list)")
    
    print(f"\n2. Custom frequency (save/visualize every 5 positions):")
    print(f"   results_df, analyzer = run_iterative_deepening_analysis(fen_list, save_visualize_frequency=5)")
    
    print(f"\n3. Analyze single position:")
    print(f"   depth_results = analyze_single_fen(fen_string)")
    
    print(f"\n📁 Output Structure:")
    print(f"analysis_sessions/session_name/")
    print(f"├── checkpoints/")
    print(f"│   ├── checkpoint_10_positions_YYYYMMDD_HHMMSS.csv")
    print(f"│   ├── checkpoint_10_depth_1_YYYYMMDD_HHMMSS.csv")
    print(f"│   ├── checkpoint_20_positions_YYYYMMDD_HHMMSS.csv")
    print(f"│   └── ...")
    print(f"├── visualize/")
    print(f"│   ├── progress_10_positions_YYYYMMDD_HHMMSS.png")
    print(f"│   ├── progress_20_positions_YYYYMMDD_HHMMSS.png")
    print(f"│   ├── depth_1_analysis.png         # Final individual depth analysis")
    print(f"│   ├── depth_2_analysis.png")
    print(f"│   ├── ...")
    print(f"│   └── comprehensive_analysis.png   # Final summary trends & scaling")
    print(f"├── iterative_analysis_YYYYMMDD_HHMMSS.csv")
    print(f"└── depth_N_results.csv")
    
    # Uncomment to run analysis
    print(f"\n🚀 Starting analysis with checkpoints every 10 positions...")
    results_df, analyzer = run_iterative_deepening_analysis(
        fen_list=sample_fen_list,
        session_name="iterative_demo_10pos",
        max_depth=9,
        save_visualize_frequency=10  # Save and visualize every 10 positions
    )