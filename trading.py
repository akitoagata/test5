"""
Trading operations and binary options logic
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Trade, Portfolio, Holding, Transaction, MarketData
from market_data import MarketDataProvider
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

trading_bp = Blueprint('trading', __name__, url_prefix='/trading')

@trading_bp.route('/markets')
def markets():
    """View live markets"""
    try:
        market_data = MarketDataProvider.get_all_market_data()
        
        # Organize by asset type
        organized_data = {
            'crypto': {},
            'stocks': {},
            'commodities': {}
        }
        
        crypto_symbols = ['BTC', 'ETH']
        stock_symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT']
        commodity_symbols = ['GOLD', 'CRUDE_OIL']
        
        for symbol, data in market_data.items():
            if symbol in crypto_symbols:
                organized_data['crypto'][symbol] = data
            elif symbol in stock_symbols:
                organized_data['stocks'][symbol] = data
            elif symbol in commodity_symbols:
                organized_data['commodities'][symbol] = data
        
        return render_template('trading/markets.html', market_data=organized_data)
    
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")
        flash('Error loading market data', 'error')
        return render_template('trading/markets.html', market_data={})

@trading_bp.route('/api/markets')
def api_markets():
    """API endpoint for market data (JSON)"""
    try:
        market_data = MarketDataProvider.get_all_market_data()
        
        # Convert datetime objects to strings for JSON
        formatted_data = {}
        for symbol, data in market_data.items():
            formatted_data[symbol] = {
                'symbol': data['symbol'],
                'price': data['price'],
                'high_24h': data['high_24h'],
                'low_24h': data['low_24h'],
                'volume_24h': data['volume_24h'],
                'change_24h': data['change_24h'],
                'change_percentage_24h': data['change_percentage_24h'],
                'timestamp': data['timestamp'].isoformat()
            }
        
        return jsonify(formatted_data)
    
    except Exception as e:
        logger.error(f"API market data error: {e}")
        return jsonify({'error': 'Failed to fetch market data'}), 500

@trading_bp.route('/place-trade', methods=['GET', 'POST'])
@login_required
def place_trade():
    """Place a binary options trade"""
    try:
        if request.method == 'POST':
            asset_type = request.form.get('asset_type', '').strip()
            asset_symbol = request.form.get('asset_symbol', '').strip()
            trade_type = request.form.get('trade_type', '').strip()  # call or put
            amount = request.form.get('amount', '0')
            expiration = request.form.get('expiration', '5')  # minutes
            
            # Validation
            try:
                amount = float(amount)
                expiration = int(expiration)
            except ValueError:
                flash('Invalid amount or expiration', 'error')
                return redirect(url_for('trading.place_trade'))
            
            if amount <= 0:
                flash('Amount must be greater than 0', 'error')
                return redirect(url_for('trading.place_trade'))
            
            if amount > current_user.account_balance:
                flash('Insufficient balance', 'error')
                return redirect(url_for('trading.place_trade'))
            
            if trade_type not in ['call', 'put']:
                flash('Invalid trade type', 'error')
                return redirect(url_for('trading.place_trade'))
            
            if expiration < 1 or expiration > 1440:  # 1 minute to 24 hours
                flash('Expiration must be between 1 and 1440 minutes', 'error')
                return redirect(url_for('trading.place_trade'))
            
            # Get current price
            price_data = None
            if asset_type == 'crypto':
                price_data = MarketDataProvider.get_crypto_price(asset_symbol)
            elif asset_type == 'stock':
                price_data = MarketDataProvider.get_stock_price(asset_symbol)
            elif asset_type == 'commodity':
                price_data = MarketDataProvider.get_commodity_price(asset_symbol)
            
            if not price_data:
                flash('Unable to fetch current price', 'error')
                return redirect(url_for('trading.place_trade'))
            
            # Create trade
            expiration_time = datetime.utcnow() + timedelta(minutes=expiration)
            
            trade = Trade(
                user_id=current_user.id,
                asset_type=asset_type,
                asset_symbol=asset_symbol,
                trade_type=trade_type,
                entry_price=price_data['price'],
                amount=amount,
                expiration_time=expiration_time,
                status='open'
            )
            
            # Deduct amount from balance
            current_user.account_balance -= amount
            
            # Log transaction
            transaction = Transaction(
                user_id=current_user.id,
                transaction_type='trade_placed',
                amount=-amount,
                status='completed',
                description=f'Binary trade on {asset_symbol}'
            )
            
            db.session.add(trade)
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"Trade placed by {current_user.username}: {asset_symbol} {trade_type} ${amount}")
            flash(f'Trade placed successfully: {asset_symbol} {trade_type.upper()} for ${amount}', 'success')
            return redirect(url_for('trading.active_trades'))
        
        return render_template('trading/place_trade.html')
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Trade placement error: {e}")
        flash('An error occurred while placing trade', 'error')
        return redirect(url_for('trading.place_trade'))

@trading_bp.route('/active-trades')
@login_required
def active_trades():
    """View active trades"""
    try:
        trades = Trade.query.filter_by(user_id=current_user.id, status='open').all()
        
        # Update trade status if expired
        now = datetime.utcnow()
        for trade in trades:
            if now >= trade.expiration_time and trade.status == 'open':
                trade.status = 'expired'
        
        db.session.commit()
        
        # Fetch live prices for open trades
        for trade in trades:
            if trade.status == 'open':
                if trade.asset_type == 'crypto':
                    price_data = MarketDataProvider.get_crypto_price(trade.asset_symbol)
                elif trade.asset_type == 'stock':
                    price_data = MarketDataProvider.get_stock_price(trade.asset_symbol)
                else:
                    price_data = MarketDataProvider.get_commodity_price(trade.asset_symbol)
                
                if price_data:
                    trade.exit_price = price_data['price']
        
        return render_template('trading/active_trades.html', trades=trades)
    
    except Exception as e:
        logger.error(f"Error fetching active trades: {e}")
        flash('Error loading active trades', 'error')
        return render_template('trading/active_trades.html', trades=[])

@trading_bp.route('/trade-history')
@login_required
def trade_history():
    """View trade history"""
    try:
        page = request.args.get('page', 1, type=int)
        trades = Trade.query.filter_by(user_id=current_user.id).filter(
            Trade.status.in_(['closed', 'expired'])
        ).order_by(Trade.closed_at.desc()).paginate(page=page, per_page=20)
        
        return render_template('trading/trade_history.html', trades=trades)
    
    except Exception as e:
        logger.error(f"Error fetching trade history: {e}")
        flash('Error loading trade history', 'error')
        return render_template('trading/trade_history.html', trades=[])

@trading_bp.route('/api/close-trade/<trade_id>', methods=['POST'])
@login_required
def api_close_trade(trade_id):
    """API endpoint to close a trade"""
    try:
        trade = Trade.query.filter_by(id=trade_id, user_id=current_user.id).first()
        
        if not trade:
            return jsonify({'error': 'Trade not found'}), 404
        
        if trade.status != 'open':
            return jsonify({'error': 'Trade is not open'}), 400
        
        # Get current price
        if trade.asset_type == 'crypto':
            price_data = MarketDataProvider.get_crypto_price(trade.asset_symbol)
        elif trade.asset_type == 'stock':
            price_data = MarketDataProvider.get_stock_price(trade.asset_symbol)
        else:
            price_data = MarketDataProvider.get_commodity_price(trade.asset_symbol)
        
        if not price_data:
            return jsonify({'error': 'Unable to fetch current price'}), 500
        
        trade.exit_price = price_data['price']
        trade.calculate_result(price_data['price'])
        trade.status = 'closed'
        trade.closed_at = datetime.utcnow()
        
        # Update balance
        if trade.pnl > 0:
            current_user.account_balance += trade.pnl
        
        # Update portfolio
        if not current_user.portfolio:
            portfolio = Portfolio(user_id=current_user.id)
            db.session.add(portfolio)
            db.session.flush()
        
        db.session.commit()
        
        logger.info(f"Trade closed by {current_user.username}: {trade.id} - Result: {trade.result}")
        
        return jsonify({
            'success': True,
            'result': trade.result,
            'pnl': trade.pnl,
            'exit_price': trade.exit_price
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error closing trade: {e}")
        return jsonify({'error': 'Failed to close trade'}), 500

@trading_bp.route('/portfolio')
@login_required
def portfolio():
    """View portfolio"""
    try:
        if not current_user.portfolio:
            portfolio = Portfolio(user_id=current_user.id)
            db.session.add(portfolio)
            db.session.commit()
        
        portfolio = current_user.portfolio
        holdings = portfolio.holdings.all()
        
        # Calculate stats
        total_value = portfolio.get_total_value()
        
        # Calculate win rate
        closed_trades = Trade.query.filter_by(
            user_id=current_user.id,
            status='closed'
        ).all()
        
        if closed_trades:
            wins = sum(1 for t in closed_trades if t.result == 'win')
            win_rate = (wins / len(closed_trades)) * 100
            portfolio.win_rate = win_rate
        
        return render_template('trading/portfolio.html', portfolio=portfolio, holdings=holdings)
    
    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}")
        flash('Error loading portfolio', 'error')
        return render_template('trading/portfolio.html', portfolio=None, holdings=[])
