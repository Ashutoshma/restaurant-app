"""Forms for reviews and ratings"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ReviewForm(FlaskForm):
    """Form for submitting restaurant reviews"""
    
    rating = IntegerField(
        'Rating',
        validators=[
            DataRequired(message='Rating is required'),
            NumberRange(min=1, max=5, message='Rating must be between 1 and 5 stars')
        ],
        render_kw={
            'class': 'form-control',
            'min': '1',
            'max': '5',
            'type': 'number'
        }
    )
    
    text = TextAreaField(
        'Your Review',
        validators=[
            DataRequired(message='Review text is required'),
            Length(min=10, max=500, message='Review must be between 10 and 500 characters')
        ],
        render_kw={
            'class': 'form-control',
            'rows': '4',
            'placeholder': 'Share your dining experience...'
        }
    )
    
    submit = SubmitField('Submit Review', render_kw={'class': 'btn btn-primary'})
