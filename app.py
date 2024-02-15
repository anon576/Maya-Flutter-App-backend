from routes import app

if __name__ == "__main__":

    # Run the Flask app
    app.run(host='10.0.2.2', port=5000,debug=True)