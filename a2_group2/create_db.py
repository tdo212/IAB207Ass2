from SeminarHub import create_app, db
from SeminarHub.models import User, Event, Comment, Booking
from datetime import datetime, date, time
from flask_bcrypt import generate_password_hash
import os
import random
import string

def generate_booking_number():
    """generate a unique booking number."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

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
                    first_name="John",
                    last_name="Doe",
                    email="john.doe@example.edu",
                    password_hash=generate_password_hash("password123").decode('utf-8'),
                    number="0412345678",
                    address="123 University Ave"
                ),
                User(
                    first_name="Jane",
                    last_name="Doe",
                    email="jane.doe@example.com",
                    password_hash=generate_password_hash("password123").decode('utf-8'),
                    number="0423456789",
                    address="456 College St"
                ),
                User(
                    first_name="Jim",
                    last_name="Doe",
                    email="jim.doe@example.com.au",
                    password_hash=generate_password_hash("password123").decode('utf-8'),
                    number="0434567890",
                    address="789 Academic Lane"
                ),
                User(
                    first_name="Jenny",
                    last_name="Doe",
                    email="jenny.doe@university.edu",
                    password_hash=generate_password_hash("password123").decode('utf-8'),
                    number="0445678901",
                    address="321 Campus Road"
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
                    location="Main Auditorium, University Campus, Education City",
                    capacity=60,
                    status="Open",
                    start_dt=datetime(2025, 10, 15, 14, 0, 0),
                    end_dt=datetime(2025, 10, 15, 16, 30, 0),
                    image_url="https://images.unsplash.com/photo-1581094794329-c8112a89af12?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
                    speaker_bio="Expert in AI and machine learning with 15 years of experience.",
                    owner_user_id=1,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Digital Marketing Strategies",
                    description="Learn how to leverage digital platforms for business growth. This seminar covers social media marketing, SEO, content strategy, and data analytics for modern businesses.",
                    category="Business",
                    speaker="Professor Man",
                    location="Business Building Room 304, Business Faculty, University Campus",
                    capacity=40,
                    status="Open",
                    start_dt=datetime(2026, 10, 20, 10, 0, 0),
                    end_dt=datetime(2026, 10, 20, 12, 0, 0),
                    image_url="https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    speaker_bio="Digital marketing strategist and business consultant.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Advances in Neuroscience",
                    description="Cutting-edge research and developments in brain science. Explore the latest discoveries in neural pathways, cognitive function, and therapeutic applications.",
                    category="Medicine",
                    speaker="Dr. Coops",
                    location="Medical Sciences Building, Health Sciences Campus",
                    capacity=30,
                    status="Sold Out",
                    start_dt=datetime(2024, 10, 22, 15, 30, 0),
                    end_dt=datetime(2024, 10, 22, 18, 0, 0),
                    image_url="https://images.unsplash.com/photo-1566669419640-ae09e20a18d8?q=80&w=1074&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    speaker_bio="Neuroscience researcher and medical practitioner.",
                    owner_user_id=1,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Renewable Energy Solutions",
                    description="Innovations in sustainable energy and green technology. This seminar discusses solar, wind, and hydroelectric power advancements for a sustainable future.",
                    category="Engineering",
                    speaker="Dr. Cooper B",
                    location="Engineering Building Atrium, Engineering Faculty, University Campus",
                    capacity=50,
                    status="Open",
                    start_dt=datetime(2027, 10, 25, 11, 0, 0),
                    end_dt=datetime(2027, 10, 25, 13, 0, 0),
                    image_url="https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    speaker_bio="Renewable energy engineer and researcher.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Global Economic Trends",
                    description="Analysis of current economic patterns and future predictions. Understand global markets, trade relationships, and economic indicators shaping our world.",
                    category="Social Sciences",
                    speaker="Dr. Khai",
                    location="Social Sciences Lecture Hall, Social Sciences Building",
                    capacity=45,
                    status="Open",
                    start_dt=datetime(2028, 11, 5, 13, 30, 0),
                    end_dt=datetime(2028, 11, 5, 15, 30, 0),
                    image_url="https://images.unsplash.com/photo-1532094349884-543bc11b234d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    speaker_bio="Economist and global trends analyst.",
                    owner_user_id=1,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Leadership in Tech Industries",
                    description="Strategies for effective leadership in technology companies. Learn from successful tech leaders about team management, innovation, and driving growth in fast-paced environments.",
                    category="Business",
                    speaker="Dr. Ash",
                    location="Conference Hall B, Business Faculty, University Campus",
                    capacity=35,
                    status="Sold Out",
                    start_dt=datetime(2024, 9, 30, 9, 0, 0),
                    end_dt=datetime(2024, 9, 30, 11, 0, 0),
                    image_url="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    speaker_bio="Tech industry executive and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="How to plan your career",
                    description="Determine your career path with effective planning strategies. This seminar will guide you through setting goals, identifying opportunities, and building a roadmap for professional success.",
                    category="Business",
                    speaker="Dr. Singh",
                    location="A Block Theatre, Business Faculty, University Campus",
                    capacity=55,
                    status="Open",
                    start_dt=datetime(2025, 11, 27, 11, 0, 0),
                    end_dt=datetime(2025, 11, 27, 13, 0, 0),
                    image_url="https://images.unsplash.com/photo-1507679799987-c73779587ccf?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1171",
                    speaker_bio="Career consultant and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Advanced Data Science Techniques",
                    description="Deep dive into advanced data science methodologies. Explore machine learning algorithms, big data processing, and statistical modeling for real-world applications.",
                    category="Computer Science",
                    speaker="Dr. Ash",
                    location="Conference Hall B, Business Faculty, University Campus",
                    capacity=122,
                    status="Open",
                    start_dt=datetime(2025, 11, 23, 15, 0, 0),
                    end_dt=datetime(2025, 11, 23, 16, 0, 0),
                    image_url="https://images.unsplash.com/photo-1666875753105-c63a6f3bdc86?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1173",
                    speaker_bio="Tech industry executive and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Cybersecurity in the Modern Age",
                    description="Cybersecurity challenges and solutions for today's digital world. Learn about threat detection, risk management, and best practices for protecting information systems.",
                    category="Computer Science",
                    speaker="Dr. Dash",
                    location="Theatre 3, Business Faculty, University Campus",
                    capacity=255,
                    status="Open",
                    start_dt=datetime(2025, 11, 6, 18, 0, 0),
                    end_dt=datetime(2025, 11, 6, 22, 30, 0),
                    image_url="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",
                    speaker_bio="Tech industry executive and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),

                Event(
                    title="Emerging Technologies in FinTech",
                    description="FinTech innovations transforming the financial industry. Explore blockchain, digital payments, and AI-driven financial services shaping the future of finance.",
                    category="Computer Science",
                    speaker="Emma Lee",
                    location="Lecture Hall D11, Business Faculty, University Campus",
                    capacity=77,
                    status="Open",
                    start_dt=datetime(2025, 11, 1, 9, 0, 0),
                    end_dt=datetime(2025, 11, 1, 12, 0, 0),
                    image_url="https://images.unsplash.com/photo-1559526324-593bc073d938?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",
                    speaker_bio="Tech industry executive and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Mentorship in Modern Workplaces",
                    description="Strategies for effective leadership in technology companies. Learn from successful tech leaders about team management, innovation, and driving growth in fast-paced environments.",
                    category="Social Sciences",
                    speaker="Dr. Ash",
                    location="Conference Hall Z, Business Faculty, University Campus",
                    capacity=95,
                    status="Open",
                    start_dt=datetime(2025, 10, 30, 9, 0, 0),
                    end_dt=datetime(2025, 10, 30, 11, 0, 0),
                    image_url="https://images.unsplash.com/photo-1522881193457-37ae97c905bf?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",
                    speaker_bio="Tech industry executive and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Stock Market Investing Basics",
                    description="Stock market fundamentals and investment strategies for beginners. Learn how to analyze stocks, build a diversified portfolio, and navigate market fluctuations.",
                    category="Business",
                    speaker="Alice Wong",
                    location="A3 Meeting Room, University Campus",
                    capacity=55,
                    status="Open",
                    start_dt=datetime(2025, 11, 19, 11, 0, 0),
                    end_dt=datetime(2025, 11, 19, 13, 0, 0),
                    image_url="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",
                    speaker_bio="Career consultant and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Chemical Engineering Innovations",
                    description="chemical engineering breakthroughs and their applications. Explore new materials, processes, and technologies driving advancements in the chemical industry.",
                    category="Engineering",
                    speaker="Dr. Singh",
                    location="Conference Hall B, Science Faculty, University Campus",
                    capacity=122,
                    status="Open",
                    start_dt=datetime(2025, 11, 23, 15, 0, 0),
                    end_dt=datetime(2025, 11, 23, 16, 0, 0),
                    image_url="https://images.unsplash.com/photo-1617155093730-a8bf47be792d?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",
                    speaker_bio="Tech industry executive and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
                Event(
                    title="Ecommerce Trends and Strategies",
                    description="Ecommerce growth and digital retail strategies. Learn about consumer behavior, online marketing, and technology trends shaping the future of ecommerce.",
                    category="Business",
                    speaker="Robert Dow",
                    location="Theatre 2, Business Faculty, University Campus",
                    capacity=255,
                    status="Open",
                    start_dt=datetime(2025, 11, 6, 18, 0, 0),
                    end_dt=datetime(2025, 11, 6, 22, 30, 0),
                    image_url="https://images.unsplash.com/photo-1664455340023-214c33a9d0bd?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZWNvbW1lcmNlfGVufDB8fDB8fHwy&auto=format&fit=crop&q=60&w=500",
                    speaker_bio="Tech industry executive and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),

                Event(
                    title="The Rise of Esports",
                    description="Explore the booming industry of esports, its cultural impact, and career opportunities. This seminar covers game development, competitive gaming, and the business side of esports.",
                    category="Business",
                    speaker="Paul Smith",
                    location="Lecture Hall A2, Entertainment Faculty, University Campus",
                    capacity=77,
                    status="Open",
                    start_dt=datetime(2025, 11, 1, 9, 0, 0),
                    end_dt=datetime(2025, 11, 1, 12, 0, 0),
                    image_url="https://images.unsplash.com/photo-1542751371-adc38448a05e?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",
                    speaker_bio="Tech industry executive and leadership coach.",
                    owner_user_id=4,
                    date_added = datetime(2025, 10, 1, 14, 0, 0)  # manually set
                ),
            ]
            
            db.session.add_all(events)
            db.session.commit()
            print("Added dummy events!")
        
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
        
        # check if bookings already exist.
        if Booking.query.count() == 0:
            # create some bookings.
            bookings = [
                Booking(
                    booking_number=generate_booking_number(),
                    quantity=2,
                    booking_date=datetime(2025, 10, 1, 10, 30, 0),
                    status="Confirmed",
                    user_id=2,
                    event_id=1
                ),
                Booking(
                    booking_number=generate_booking_number(),
                    quantity=1,
                    booking_date=datetime(2025, 9, 28, 14, 15, 0),
                    status="Confirmed",
                    user_id=3,
                    event_id=2
                ),
                Booking(
                    booking_number=generate_booking_number(),
                    quantity=3,
                    booking_date=datetime(2025, 10, 13, 11, 45, 0),
                    status="Confirmed",
                    user_id=2,
                    event_id=5
                )
            ]
            
            db.session.add_all(bookings)
            db.session.commit()
            print("Added dummy bookings!")
        
        print("Database setup complete!")

if __name__ == "__main__":
    app = create_app()
    create_database(app)
    print("Database setup complete!")
