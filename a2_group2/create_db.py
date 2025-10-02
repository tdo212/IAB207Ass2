# this is where we will create our database

'''
from SeminarHub import create_app, db
from SeminarHub.models import User, Event, Comment, Order
from datetime import datetime, date, time
from flask_bcrypt import generate_password_hash
import os

def create_database(app):
    with app.app_context():
        # create uploads directory if it doesn't exist.
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            print("Created uploads directory!")
        
        db.create_all()
        print("Created database tables!")
        
        # check if users already exist.
        if User.query.count() == 0:
            # create some users.
            users = [
                User(
                    name="John Doe",
                    email="john.doe@example.edu",
                    password_hash=generate_password_hash("password123").decode('utf-8'),
                    contact_number="0412345678",
                    address="123 University Ave, Brisbane"
                ),
                User(
                    name="Jane Doe",
                    email="jane.doe@example.com",
                    password_hash=generate_password_hash("password123").decode('utf-8'),
                    contact_number="0423456789",
                    address="456 College St, Brisbane"
                ),
                User(
                    name="Jim Doe",
                    email="jim.doe@example.com.au",
                    password_hash=generate_password_hash("password123").decode('utf-8'),
                    contact_number="0434567890",
                    address="789 Academic Lane, Brisbane"
                ),
                User(
                    name="Jenny Doe",
                    email="jenny.doe@university.edu",
                    password_hash=generate_password_hash("password123").decode('utf-8'),
                    contact_number="0445678901",
                    address="321 Campus Road, Brisbane"
                )
            ]
            
            db.session.add_all(users)
            db.session.commit()
            print("Added dummy users!")
        
        # check if events already exist.
        if Event.query.count() == 0:
            # create some events.
            events = [
                Event(
                    title="Future of Artificial Intelligence",
                    description="This seminar will explore the cutting-edge developments in artificial intelligence and machine learning. Our expert panel will discuss the ethical implications, future applications, and potential impacts of AI on various industries.",
                    category="Computer Science",
                    speaker="Dr. Guy",
                    date=date(2025, 10, 15),
                    start_time=time(14, 0),
                    end_time=time(16, 30),
                    venue="Main Auditorium",
                    venue_address="University Campus, Education City",
                    capacity=60,
                    tickets_available=47,
                    # free seminar.
                    price=0.0,  
                    image_url="https://images.unsplash.com/photo-1581094794329-c8112a89af12?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
                    user_id=1  
                ),
                Event(
                    title="Digital Marketing Strategies",
                    description="Learn how to leverage digital platforms for business growth. This seminar covers social media marketing, SEO, content strategy, and data analytics for modern businesses.",
                    category="Business",
                    speaker="Professor Man",
                    date=date(2026, 10, 20),
                    start_time=time(10, 0),
                    end_time=time(12, 0),
                    venue="Business Building Room 304",
                    venue_address="Business Faculty, University Campus",
                    capacity=40,
                    tickets_available=12,
                    price=25.0,
                    image_url="https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    user_id=4
                ),
                Event(
                    title="Advances in Neuroscience",
                    description="Cutting-edge research and developments in brain science. Explore the latest discoveries in neural pathways, cognitive function, and therapeutic applications.",
                    category="Medicine",
                    speaker="Dr. Coops",
                    date=date(2024, 10, 22),
                    start_time=time(15, 30),
                    end_time=time(18, 0),
                    venue="Medical Sciences Building",
                    venue_address="Health Sciences Campus",
                    capacity=30,
                     # sold out.
                    tickets_available=0, 
                    price=15.0,
                    image_url="https://images.unsplash.com/photo-1576091160399-112ba8d25d15?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    user_id=1
                ),
                Event(
                    title="Renewable Energy Solutions",
                    description="Innovations in sustainable energy and green technology. This seminar discusses solar, wind, and hydroelectric power advancements for a sustainable future.",
                    category="Engineering",
                    speaker="Dr. Cooper B",
                    date=date(2027, 10, 25),
                    start_time=time(11, 0),
                    end_time=time(13, 0),
                    venue="Engineering Building Atrium",
                    venue_address="Engineering Faculty, University Campus",
                    capacity=50,
                    tickets_available=35,
                    price=0.0,
                    image_url="https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    user_id=4
                ),
                Event(
                    title="Global Economic Trends",
                    description="Analysis of current economic patterns and future predictions. Understand global markets, trade relationships, and economic indicators shaping our world.",
                    category="Social Sciences",
                    speaker="Dr. Khai",
                    date=date(2028, 11, 5),
                    start_time=time(13, 30),
                    end_time=time(15, 30),
                    venue="Social Sciences Lecture Hall",
                    venue_address="Social Sciences Building",
                    capacity=45,
                    tickets_available=28,
                    price=10.0,
                    image_url="https://images.unsplash.com/photo-1532094349884-543bc11b234d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    user_id=1
                ),
                Event(
                    title="Leadership in Tech Industries",
                    description="Strategies for effective leadership in technology companies. Learn from successful tech leaders about team management, innovation, and driving growth in fast-paced environments.",
                    category="Business",
                    speaker="Dr. Ash",
                    date=date(2024, 9, 30),
                    start_time=time(9, 0),
                    end_time=time(11, 0),
                    venue="Conference Hall B",
                    venue_address="Business Faculty, University Campus",
                    capacity=35,
                    tickets_available=0,
                    price=20.0,
                    image_url="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    user_id=4
                )
            ]
            
            db.session.add_all(events)
            db.session.commit()
            print("Added dummy events!")
            
            # update event statuses.
            for event in events:
                event.update_status()
            db.session.commit()
        
        # check if comments already exist.
        if Comment.query.count() == 0:
            # create some comments.
            comments = [
                Comment(
                    text="Looking forward to this event! Will there be any discussion about AI regulation frameworks?",
                    user_id=2,  
                    event_id=1,  
                    created_at=datetime(2025, 10, 5, 14, 30, 0)
                ),
                Comment(
                    text="This work on ethical AI is groundbreaking. Can't wait to hear some insights.",
                    user_id=3,  
                    event_id=1,  
                    created_at=datetime(2025, 10, 3, 9, 15, 0)
                ),
                Comment(
                    text="Are there any prerequisites for attending this seminar?",
                    user_id=2, 
                    event_id=2,  
                    created_at=datetime(2025, 9, 28, 16, 45, 0)
                ),
                Comment(
                    text="This seminar was incredibly informative! The speaker was very engaging.",
                    user_id=3, 
                    event_id=6,  
                    created_at=datetime(2024, 9, 15, 11, 20, 0)
                )
            ]
            
            db.session.add_all(comments)
            db.session.commit()
            print("Added dummy comments!")
        
        # check if orders already exist.
        if Order.query.count() == 0:
            # create some orders.
            orders = [
                Order(
                    quantity=2,
                    total_price=0.0,
                    ticket_type="General Admission",
                    user_id=2,  
                    event_id=1,  
                    order_date=datetime(2025, 10, 1, 10, 30, 0)
                ),
                Order(
                    quantity=1,
                    total_price=25.0,
                    ticket_type="General Admission",
                    user_id=3,  
                    event_id=2,  
                    order_date=datetime(2025, 9, 28, 14, 15, 0)
                ),
                Order(
                    quantity=3,
                    total_price=30.0,
                    ticket_type="General Admission",
                    user_id=2,  
                    event_id=5,  
                    order_date=datetime(2025, 10, 13, 11, 45, 0)
                ),
                Order(
                    quantity=2,
                    total_price=40.0,
                    ticket_type="VIP",
                    user_id=3,  
                    event_id=6,  
                    order_date=datetime(2024, 9, 10, 9, 30, 0)
                ),
                Order(
                    quantity=1,
                    total_price=7.5,
                    ticket_type="Student",
                    user_id=2,  
                    event_id=3,  
                    order_date=datetime(2024, 9, 20, 16, 0, 0)
                )
            ]
            
            db.session.add_all(orders)
            db.session.commit()
            print("Added dummy orders!")
        
        print("Database setup complete!")

if __name__ == "__main__":
    app = create_app()
    create_database(app)
    print("Database setup complete!")
'''
