"""Forms for order creation and management"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class OrderForm(FlaskForm):
    """Form for creating orders with delivery details"""
    
    delivery_address = StringField(
        'Delivery Address',
        validators=[DataRequired(message='Delivery address is required'), Length(min=10, max=255)],
        render_kw={'class': 'form-control', 'placeholder': 'Enter your delivery address'}
    )
    
    special_instructions = TextAreaField(
        'Special Instructions (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={'class': 'form-control', 'placeholder': 'Any special requests or allergies?', 'rows': 3}
    )
    
    notes = TextAreaField(
        'Order Notes (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={'class': 'form-control', 'placeholder': 'Additional notes about your order', 'rows': 2}
    )
    
    submit = SubmitField('Place Order', render_kw={'class': 'btn btn-primary btn-lg w-100'})
