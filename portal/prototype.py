from flask import Flask, render_template, redirect, request, jsonify, url_for, flash
import re
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10002)
