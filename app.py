import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath

UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads/')

app = Flask(__name__)
app.config['UPLOADS_PATH'] = UPLOADS_PATH

db_path = 'C:\\Users\\gamin\\OneDrive\\Desktop\\interview\\projects\\foodima\\db.db'
def create_connection():
  conn = sqlite3.connect(db_path)
  return conn

@app.route('/')
def index():
  conn = create_connection()
  with conn:
    sql = ''' select * from recipes '''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    recipes = cur.fetchall()
    recipes_ing = {}
    for i in recipes:
      sql = ''' SELECT ingredients.ing_name from recipes
            INNER JOIN made_of on  recipes.recipe_id = made_of.recipe_id 
            INNER JOIN ingredients on made_of.ing_id = ingredients.ing_id WHERE recipes.recipe_id = ?; '''
      cur = conn.cursor()
      cur.execute(sql, [i[0]])
      conn.commit()
      ingrediants = [list(ing)[0] for ing in cur.fetchall()]
      recipes_ing[i[0]] = ingrediants
  return render_template('index.html', recipes=recipes , recipes_ing = recipes_ing)

@app.route('/about-us')
def about():
  return render_template('about-us.html')

@app.route('/add-recipes', methods = ['GET'])
def add_recipes():
  return render_template('add-recipes.html')

@app.route('/add-recipes', methods = ['POST'])
def add_recipe():
  if request.method == 'POST':
    recipe_name = request.form['recipe-name']
    ingrediants = request.form.getlist('ingrediants')
    recipe_description = request.form['recipe-description']
    recipe_img = request.files['recipe-img']

    if recipe_name != '' and len(ingrediants) != 0 and recipe_description != '':
      conn = create_connection()
      with conn:
        if recipe_img.filename != '' and recipe_img:
          filename = secure_filename(recipe_img.filename)
          recipe_img.save(os.path.join(app.config['UPLOADS_PATH'], filename))

          # insert recipe
          sql = ''' INSERT INTO recipes(recipe_name, recipe_desc, recipe_image) VALUES(?,?,?) '''
          cur = conn.cursor()
          recipe = (recipe_name, recipe_description, recipe_img.filename)
          cur.execute(sql, recipe)
          conn.commit()
          recipe_id = cur.lastrowid

          # get ingrediants ids
          ing_ids = []
          for ing_name in ingrediants:
            sql = ''' select ing_id from ingredients where ing_name = ? '''
            cur = conn.cursor()
            cur.execute(sql, [ing_name])
            conn.commit()
            ing_ids.append(cur.fetchone()[0])
          
          # insert to made_of table
          ing_ids = list(ing_ids)
          for ing_id in ing_ids:
            sql = ''' INSERT INTO made_of(recipe_id, ing_id) VALUES(?,?) '''
            cur = conn.cursor()
            ing_id = int(ing_id)
            recipe_id  = int(recipe_id)
            made_of_record = [recipe_id, ing_id]
            cur.execute(sql, made_of_record)
            conn.commit()

          return redirect(url_for('index'))
          
  return redirect(url_for('add_recipes'))

@app.route('/sign-in')
def sign_in():
  return render_template('sign-in.html')

@app.route('/sign-up')
def sign_up():
  return render_template('sign-up.html')

@app.route('/recipe/<int:recipe_id>')
def show_recipe(recipe_id):
    if recipe_id:
      conn = create_connection()
      sql = ''' SELECT * from recipes WHERE recipe_id = ?; '''
      cur = conn.cursor()
      cur.execute(sql, [recipe_id])
      conn.commit()
      recipe = cur.fetchone()
      sql = ''' SELECT ingredients.ing_name from recipes
            INNER JOIN made_of on  recipes.recipe_id = made_of.recipe_id 
            INNER JOIN ingredients on made_of.ing_id = ingredients.ing_id WHERE recipes.recipe_id = ?; '''
      cur = conn.cursor()
      cur.execute(sql, [recipe_id])
      conn.commit()
      ingrediants = [list(ing)[0] for ing in cur.fetchall()]
      print(ingrediants)
      return render_template('recipe.html', recipe = recipe , ingrediants = ingrediants)
    else:
      return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)