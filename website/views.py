from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import text
from .models import Review, Restaurant
from . import db
views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    reviews = Review.query.all()
    return render_template("home.html", user=current_user, reviews=reviews)

@views.route("/create-review", methods=['GET', 'POST'])
@login_required
def create_review():
    if request.method == "POST":
        text = request.form.get('text')
        restaurant_id = request.form.get('restaurant_id')
        rating = request.form.get('rating')

        # Input validations
        if not text:
            flash('Review cannot be empty', category='error')
        elif not restaurant_id:
            flash('Please select a location', category='error')
        elif not rating:
            flash('Please select a rating', category='error')
        else:
            # Create the review object
            review = Review(
                text=text,
                restaurant_id=restaurant_id,
                rating=int(rating),
                author=current_user.id
            )
            db.session.add(review)
            db.session.commit()
            flash('Review created!', category='success')
            return redirect(url_for('views.home'))
    
    restaurants = Restaurant.query.all()
    return render_template("create_review.html", user=current_user, restaurants=restaurants)

@views.route("/add-restaurant", methods=['GET', 'POST'])
@login_required
def add_restaurant():
    if request.method == "POST":
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')

        if not name or not address or not city or not state:
            flash('Please provide all required fields.', category='error')
        else:
            # Create a new restaurant object using ORM
            new_restaurant = Restaurant(
                name=name,
                address=address,
                city=city,
                state=state
            )
            db.session.add(new_restaurant)
            db.session.commit()
            flash('Restaurant added successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("add_restaurant.html")

@views.route("/edit-review/<int:id>", methods=["GET", "POST"])
@login_required
def edit_review(id):
    review = Review.query.filter_by(id=id).first()

    if not review:
        flash("Review does not exist.", category="error")
        return redirect(url_for("views.home"))

    if current_user.id != review.author:
        flash("You do not have permission to edit this review.", category="error")
        return redirect(url_for("views.home"))

    if request.method == "POST":
        text = request.form.get("text")
        rating = request.form.get("rating")
        restaurant_id = request.form.get("restaurant_id")

        if not text:
            flash("Review text cannot be empty.", category="error")
        elif not rating:
            flash("Please select a rating.", category="error")
        else:
            try:
                review.text = text
                review.rating = int(rating)
                if restaurant_id:
                    review.restaurant_id = int(restaurant_id)

                db.session.commit()
                flash("Review updated successfully!", category="success")
                return redirect(url_for("views.home"))
            except Exception as e:
                db.session.rollback()  # Rollback on failure to ensure consistency
                flash(f"An error occurred: {str(e)}", category="error")

    restaurants = Restaurant.query.all() 
    return render_template("create_review.html", review=review, restaurants=restaurants)
    

@views.route("/report", methods=["GET"])
@login_required
def report():
    #prepared statement
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(author=current_user.id).scalar()
    
    #ORM
    most_reviewed = (
        db.session.query(Restaurant.name, db.func.count(Review.id).label("review_count"))
        .join(Review, Review.restaurant_id == Restaurant.id)
        .filter(Review.author == current_user.id)
        .group_by(Restaurant.name)
        .order_by(db.desc("review_count"))
        .first()
    )
    
    
    # Extract most reviewed details
    most_reviewed_name = most_reviewed[0] if most_reviewed else None
    most_reviewed_count = most_reviewed[1] if most_reviewed else 0

    return render_template(
        "report.html",
        avg_rating=avg_rating,
        most_reviewed_name=most_reviewed_name,
        most_reviewed_count=most_reviewed_count,
    )

@views.route("/delete-review/<id>")
@login_required
def delete_review(id):
    review = Review.query.filter_by(id=id).first()

    if not review:
        flash("Review does not exist.", category='error')
    elif current_user.id != review.author:
        flash('You do not have permission to delete this review.', category='error')
    else:
        db.session.delete(review)
        db.session.commit()
        flash('Review deleted.', category='success')

    return redirect(url_for('views.home'))

