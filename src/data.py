"""
Data management module for ZerodhaWise.

This module provides data fetching, storage, and processing functionality
for portfolio and market data.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .utils import load_config, setup_logging

Base = declarative_base()


class DataManager:
    """
    Class for managing data fetching, storage, and processing.
    
    This class provides methods to fetch data from Zerodha API,
    store data in database, and process historical data.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DataManager.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.logger = setup_logging(__name__)
        self.engine = None
        self.Session = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection."""
        try:
            db_url = self.config.get('database', {}).get('url', 'sqlite:///portfolio.db')
            self.engine = create_engine(db_url)
            self.Session = sessionmaker(bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(self.engine)
            self.logger.info("Database setup completed")
            
        except Exception as e:
            self.logger.error(f"Database setup failed: {str(e)}")
            raise
    
    def save_portfolio(self, portfolio_data: Dict[str, Any]) -> bool:
        """
        Save portfolio data to database.
        
        Args:
            portfolio_data: Dictionary containing portfolio data.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            session = self.Session()
            
            # Create portfolio record
            portfolio_record = {
                'timestamp': datetime.now(),
                'data': json.dumps(portfolio_data),
                'total_value': sum(float(h['market_value']) for h in portfolio_data.get('holdings', [])),
                'total_pnl': sum(float(h['pnl']) for h in portfolio_data.get('holdings', [])),
                'num_holdings': len(portfolio_data.get('holdings', []))
            }
            
            # Insert into database
            query = text("""
                INSERT INTO portfolio_snapshots (timestamp, data, total_value, total_pnl, num_holdings)
                VALUES (:timestamp, :data, :total_value, :total_pnl, :num_holdings)
            """)
            
            session.execute(query, portfolio_record)
            session.commit()
            session.close()
            
            self.logger.info("Portfolio data saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving portfolio data: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_historical_portfolio(self, days: int = 30) -> pd.DataFrame:
        """
        Get historical portfolio data.
        
        Args:
            days: Number of days to fetch.
            
        Returns:
            DataFrame containing historical portfolio data.
        """
        try:
            session = self.Session()
            
            # Query historical data
            query = text("""
                SELECT timestamp, total_value, total_pnl, num_holdings
                FROM portfolio_snapshots
                WHERE timestamp >= :start_date
                ORDER BY timestamp
            """)
            
            start_date = datetime.now() - timedelta(days=days)
            result = session.execute(query, {'start_date': start_date})
            
            # Convert to DataFrame
            data = []
            for row in result:
                data.append({
                    'timestamp': row.timestamp,
                    'total_value': row.total_value,
                    'total_pnl': row.total_pnl,
                    'num_holdings': row.num_holdings
                })
            
            session.close()
            
            if data:
                df = pd.DataFrame(data)
                df.set_index('timestamp', inplace=True)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching historical portfolio data: {str(e)}")
            return pd.DataFrame()
    
    def get_portfolio_details(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get detailed portfolio data for a specific date.
        
        Args:
            date: Date to fetch data for. If None, fetches latest.
            
        Returns:
            Dictionary containing portfolio details.
        """
        try:
            session = self.Session()
            
            if date is None:
                # Get latest data
                query = text("""
                    SELECT data FROM portfolio_snapshots
                    ORDER BY timestamp DESC
                    LIMIT 1
                """)
                result = session.execute(query)
            else:
                # Get data for specific date
                query = text("""
                    SELECT data FROM portfolio_snapshots
                    WHERE DATE(timestamp) = DATE(:date)
                    ORDER BY timestamp DESC
                    LIMIT 1
                """)
                result = session.execute(query, {'date': date})
            
            row = result.fetchone()
            session.close()
            
            if row:
                return json.loads(row.data)
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching portfolio details: {str(e)}")
            return {}
    
    def save_market_data(self, symbol: str, data: Dict[str, Any]) -> bool:
        """
        Save market data for a symbol.
        
        Args:
            symbol: Stock symbol.
            data: Market data dictionary.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            session = self.Session()
            
            market_record = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'data': json.dumps(data)
            }
            
            query = text("""
                INSERT INTO market_data (symbol, timestamp, data)
                VALUES (:symbol, :timestamp, :data)
            """)
            
            session.execute(query, market_record)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving market data: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_market_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        Get historical market data for a symbol.
        
        Args:
            symbol: Stock symbol.
            days: Number of days to fetch.
            
        Returns:
            DataFrame containing market data.
        """
        try:
            session = self.Session()
            
            query = text("""
                SELECT timestamp, data
                FROM market_data
                WHERE symbol = :symbol AND timestamp >= :start_date
                ORDER BY timestamp
            """)
            
            start_date = datetime.now() - timedelta(days=days)
            result = session.execute(query, {
                'symbol': symbol,
                'start_date': start_date
            })
            
            data = []
            for row in result:
                market_data = json.loads(row.data)
                market_data['timestamp'] = row.timestamp
                data.append(market_data)
            
            session.close()
            
            if data:
                df = pd.DataFrame(data)
                df.set_index('timestamp', inplace=True)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return pd.DataFrame()
    
    def export_data_to_csv(self, data: pd.DataFrame, filename: str) -> str:
        """
        Export data to CSV file.
        
        Args:
            data: DataFrame to export.
            filename: Output filename.
            
        Returns:
            Path to the exported file.
        """
        try:
            os.makedirs('data', exist_ok=True)
            filepath = os.path.join('data', filename)
            
            data.to_csv(filepath)
            self.logger.info(f"Data exported to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {str(e)}")
            return ""
    
    def import_data_from_csv(self, filename: str) -> pd.DataFrame:
        """
        Import data from CSV file.
        
        Args:
            filename: Input filename.
            
        Returns:
            DataFrame containing imported data.
        """
        try:
            filepath = os.path.join('data', filename)
            
            if not os.path.exists(filepath):
                self.logger.error(f"File not found: {filepath}")
                return pd.DataFrame()
            
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            self.logger.info(f"Data imported from {filepath}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error importing data: {str(e)}")
            return pd.DataFrame()
    
    def cleanup_old_data(self, days: int = 365) -> int:
        """
        Clean up old data from database.
        
        Args:
            days: Keep data newer than this many days.
            
        Returns:
            Number of records deleted.
        """
        try:
            session = self.Session()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Delete old portfolio snapshots
            portfolio_query = text("""
                DELETE FROM portfolio_snapshots
                WHERE timestamp < :cutoff_date
            """)
            
            portfolio_result = session.execute(portfolio_query, {'cutoff_date': cutoff_date})
            
            # Delete old market data
            market_query = text("""
                DELETE FROM market_data
                WHERE timestamp < :cutoff_date
            """)
            
            market_result = session.execute(market_query, {'cutoff_date': cutoff_date})
            
            session.commit()
            session.close()
            
            deleted_count = portfolio_result.rowcount + market_result.rowcount
            self.logger.info(f"Cleaned up {deleted_count} old records")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return 0
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary containing database statistics.
        """
        try:
            session = self.Session()
            
            # Portfolio snapshots count
            portfolio_query = text("SELECT COUNT(*) as count FROM portfolio_snapshots")
            portfolio_result = session.execute(portfolio_query)
            portfolio_count = portfolio_result.fetchone().count
            
            # Market data count
            market_query = text("SELECT COUNT(*) as count FROM market_data")
            market_result = session.execute(market_query)
            market_count = market_result.fetchone().count
            
            # Date range
            date_query = text("""
                SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date
                FROM portfolio_snapshots
            """)
            date_result = session.execute(date_query)
            date_row = date_result.fetchone()
            
            session.close()
            
            stats = {
                'portfolio_snapshots': portfolio_count,
                'market_data_records': market_count,
                'date_range': {
                    'start': date_row.min_date.isoformat() if date_row.min_date else None,
                    'end': date_row.max_date.isoformat() if date_row.max_date else None
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting database stats: {str(e)}")
            return {}
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Backup database to file.
        
        Args:
            backup_path: Path to backup file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # For SQLite, simply copy the database file
            if 'sqlite' in self.config.get('database', {}).get('url', ''):
                import shutil
                db_path = self.config['database']['url'].replace('sqlite:///', '')
                shutil.copy2(db_path, backup_path)
                self.logger.info(f"Database backed up to {backup_path}")
                return True
            else:
                self.logger.warning("Backup not implemented for non-SQLite databases")
                return False
                
        except Exception as e:
            self.logger.error(f"Error backing up database: {str(e)}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """
        Restore database from backup file.
        
        Args:
            backup_path: Path to backup file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # For SQLite, simply copy the backup file
            if 'sqlite' in self.config.get('database', {}).get('url', ''):
                import shutil
                db_path = self.config['database']['url'].replace('sqlite:///', '')
                shutil.copy2(backup_path, db_path)
                self.logger.info(f"Database restored from {backup_path}")
                return True
            else:
                self.logger.warning("Restore not implemented for non-SQLite databases")
                return False
                
        except Exception as e:
            self.logger.error(f"Error restoring database: {str(e)}")
            return False 