from flask import Flask, request, jsonify, render_template
from db import save_review, get_all_reviews
from llm import process_review
from flask import session, redirect, url_for
from db import save_review, get_all_reviews, get_filtered_reviews


app = Flask(__name__)

app.secret_key = "admin-secret-key"

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect("/admin")
        else:
            return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html")


# -----------------------------
# User Dashboard
# -----------------------------
@app.route("/", methods=["GET"])
def user_dashboard():
    return render_template("user.html")


@app.route("/api/submit-review", methods=["POST"])
def submit_review():
    data = request.get_json()

    rating = data.get("rating")
    review = data.get("review", "").strip()

    # Validation
    if not rating or rating not in [1, 2, 3, 4, 5]:
        return jsonify({"error": "Invalid rating"}), 400
    if len(review) == 0:
        return jsonify({"error": "Review cannot be empty"}), 400

    try:
        # Call LLM to process review
        result = process_review(review)
        user_reply = result.get("user_response", "")
        summary = result.get("summary", "")
        action = result.get("action", "")

        # Save to DB
        save_review(
            rating=rating,
            review=review,
            ai_response=user_reply,
            summary=summary,
            action=action
        )

        return jsonify({
            "success": True,
            "ai_response": user_reply
        })

    except Exception as e:
        print("llm error", e)
        return jsonify({
            "error": "AI service unavailable",
            "details": str(e)
        }), 500


# -----------------------------
# Admin Dashboard
# -----------------------------
@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    search = request.args.get("search", "").strip()
    rating = request.args.get("rating", "").strip()
    page = request.args.get("page", 1, type=int)

    # ✅ SAFE conversion
    rating_value = int(rating) if rating.isdigit() else None

    reviews = get_filtered_reviews(
        search=search,
        rating=rating_value,
        page=page
    )

    return render_template(
        "admin.html",
        reviews=reviews,
        page=page,
        search=search,
        rating=rating
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")



if __name__ == "__main__":
    app.run()

