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
    
    notes = TextAreaField(
        'Special Instructions & Notes (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={'class': 'form-control', 'placeholder': 'Any special requests, allergies, or additional notes?', 'rows': 3}
    )
    
    submit = SubmitField('Place Order', render_kw={'class': 'btn btn-primary btn-lg w-100'})
