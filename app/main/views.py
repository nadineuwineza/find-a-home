from flask import render_template,abort,request,redirect,url_for,flash
from . import main
from flask_login import login_required,current_user
from ..models import User,Article,Comment,Subscriber
from .forms import UpdateProfile,CommentForm,SubscriberForm
from .. import db,photos
from ..requests import getQuotes
from ..email import mail_message


@main.route('/')
def index():

    '''
    View root page function that returns the index page and its data
    '''
    getquotes = getQuotes()
    articles=Article.get_all_articles()
    popular=Article.query.order_by(Article.article_upvotes.desc()).limit(3).all()
    return render_template('index.html',getquotes = getquotes, articles=articles,popular=popular)

@main.route('/about')
def about():

    '''
    View root page function that returns the about page and its data
    '''
    return render_template('about.html')


@main.route('/profile/<username>')
@login_required
def profile(username):

    '''
    View profile page function that returns the profile details of the current user logged in
    '''
    user = User.query.filter_by(username = username).first()
    
    if user is None:
        abort(404)
 
    return render_template("profile/profile.html", user = user)



@main.route('/profile/<username>/update',methods = ['GET','POST'])
@login_required
def update_profile(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()

        flash('User bio updated')

        return redirect(url_for('main.profile',username=user.username))


    return render_template('profile/update.html',user=user,form =form)



@main.route('/profile/<username>/update/pic',methods= ['POST'])
@login_required
def update_pic(username):
    user = User.query.filter_by(username = username).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()

        flash('User pic updated')
        
    return redirect(url_for('main.profile',username=username)) 


@main.route('/article/new',methods= ['GET','POST'])
@login_required
def new_article():
    subscribers = Subscriber.query.all()
    if request.method=='POST':
        article_title=request.form['title']
        article_body=request.form['body']
        article_tag=request.form['tag']
        filename = photos.save(request.files['photo'])
        article_cover_path=f'photos/{filename}'
        
        new_article=Article(article_title=article_title,article_body=article_body,article_tag=article_tag,article_cover_path=article_cover_path,user=current_user)
        new_article.save_article()

        flash('Article added')


        for subscriber in subscribers:
            mail_message("Alert New House Posted","email/new_house",subscriber.email,new_article=new_article)
        return redirect(url_for('main.index'))
        flash('New House Posted')

        return redirect(url_for('main.index'))

    return render_template('new_article.html') 

@main.route('/articles/tag/<tag>')
@login_required
def article_by_tag(tag):

    '''
    View root page function that returns pitch category page with pitches from category selected
    '''
    articles=Article.query.filter_by(article_tag=tag).order_by(Article.posted.desc()).all()
    
    return render_template('article_by_tag.html',articles=articles,tag=tag)  

@main.route('/article_details/<article_id>', methods = ['GET','POST'])
@login_required
def article_details(article_id):

    '''
    View article details function that returns article_details and comment form
    '''

    form = CommentForm()
    article=Article.query.get(article_id)
    comments=Comment.query.filter_by(article_id=article_id).order_by(Comment.posted.desc()).all()
    
    if form.validate_on_submit():
        comment = form.comment.data
        
        # Updated comment instance
        new_comment = Comment(comment=comment,user=current_user,article=article)

        # save review method
        new_comment.save_comment()
        article.article_comments_count = article.article_comments_count+1

        db.session.add(article)
        db.session.commit()
        flash('Comment posted')
        return redirect(url_for('main.article_details',article_id=article_id))

    return render_template('article_details.html',comment_form=form,article=article,comments=comments) 


@main.route('/article_upvote/<article_id>')
@login_required
def article_upvote(article_id):
    '''
    View function to add do upvote on article like btn click
    '''
    article=Article.query.get(article_id)
    article.article_upvotes=article.article_upvotes+1
    db.session.add(article)
    db.session.commit() 
    flash('You liked this article') 
    return redirect(url_for('main.article_details',article_id=article_id)) 


@main.route('/article_downvote/<article_id>')
@login_required
def article_downvote(article_id):
    '''
    View function to add downvote on article dislike btn click
    '''
    article=Article.query.get(article_id)
    article.article_downvotes=article.article_downvotes+1
    db.session.add(article)
    db.session.commit()  
    flash('You disliked this article')
    return redirect(url_for('main.article_details',article_id=article_id))   


@main.route('/comment/delete/<comment_id>/<article_id>')
@login_required
def delete_comment(comment_id,article_id):
    comment = Comment.query.get(comment_id)
    db.session.delete(comment)
    article=Article.query.get(article_id)
    article.article_comments_count = article.article_comments_count-1
    db.session.add(article)
    db.session.commit()
    flash('You deleted a comment')
    return redirect(url_for('main.article_details',article_id=article_id))  


@main.route('/article/delete/<article_id>')
@login_required
def delete_article(article_id):
  article = Article.query.get(article_id)
  db.session.delete(article)
  db.session.commit()
  flash('You deleted an article')
  return redirect(url_for('main.index'))


@main.route('/subscribe', methods=['GET','POST'])
def subscriber():

    subscriber_form=SubscriberForm()
    article = Article.query.order_by(Article.posted.desc()).all()

    if subscriber_form.validate_on_submit():

        subscriber= Subscriber(email=subscriber_form.email.data,name = subscriber_form.name.data)

        db.session.add(subscriber)
        db.session.commit()

        mail_message("Welcome to Find a Home","email/subscriber",subscriber.email,subscriber=subscriber)

        title= "Find a home"
        return render_template('index.html',title=title, article=article)

    subscriber = Article.query.all()

    article = Article.query.all()


    return render_template('subscribe.html',subscriber=subscriber,subscriber_form=subscriber_form,article=article)

 
