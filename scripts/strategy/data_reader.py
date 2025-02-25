# scripts/strategy/data_reader.py
"""
scripts/strategy/data_reader.py
"""
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models.stock import StockDailyData
from src.database.models.stock2025 import StockDataTemp
from src.database.models.index import IndexDailyData
from src.database.models.concept import ConceptBoardData
from src.core.config import config
from src.core.logger import logger

class DataReader:
    """
    数据读取类，负责从数据库读取股票、指数和概念板块数据。
    """

    def __init__(self):
        """
        初始化数据库连接引擎和会话。
        """
        self.engine = create_engine(config.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_data(self, data_type: str, symbol, start_date: str, end_date: str) -> pd.DataFrame:
        """
        从数据库读取数据。

        参数:
            data_type: 数据类型，可选 'stock'(股票), 'index'(指数), 'concept'(概念板块)。
            symbol: 股票代码或股票代码列表。如果为 'all'，则读取所有股票的数据。
            start_date: 开始日期，格式 YYYYMMDD。
            end_date: 结束日期，格式 YYYYMMDD。

        返回:
            包含股票数据的 DataFrame。如果未找到数据，则返回一个空 DataFrame。
        """
        try:
            with self.SessionLocal() as session:
                if data_type == 'stock':
                    model = StockDailyData
                elif data_type == 'index':
                    model = IndexDailyData
                elif data_type == 'concept':
                    model = ConceptBoardData
                elif data_type == 'temp':
                    model = StockDataTemp
                else:
                    logger.error(f"无效的数据类型: {data_type}")
                    return pd.DataFrame()

                query = session.query(model).filter(model.date >= start_date, model.date <= end_date)

                if symbol == 'all':
                    print("执行全量查询")
                    # 先检查总记录数
                    count = query.count()
                    print(f"符合日期条件的总记录数: {count}")
                elif isinstance(symbol, list):
                    print(f"查询特定股票列表: {len(symbol)} 只股票")
                    query = query.filter(model.symbol.in_(symbol))
                else:
                    print(f"查询单个股票: {symbol}")
                    query = query.filter(model.symbol == symbol)

                # 执行查询前打印 SQL
                print("执行的 SQL 查询:")
                print(query.statement)

                df = pd.read_sql(query.statement, session.bind)
                print(f"查询结果数据量: {len(df)}")

                if not df.empty:
                    return df
                else:
                    logger.info(f"未找到 {data_type} {symbol} 在 {start_date} 和 {end_date} 之间的数据。")
                    return pd.DataFrame()

        except Exception as e:
            logger.error(f"读取数据时发生错误: {e}")
            return pd.DataFrame()