import asyncio
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db
from app.models.faculty_user import FacultyUser
from app.models.exam import Exam, Section, Question, MCQOption, TestCase, ProctoringConfig
from app.core.security import hash_password

async def main():
    print('?? Initializing DB for Seed...')
    await init_db()
    
    faculty = await FacultyUser.find_one(FacultyUser.role == 'faculty')
    if not faculty:
        print('?? Creating default faculty user...')
        faculty = FacultyUser(
            email='faculty@proxm.io',
            name='Demo Faculty',
            password_hash=hash_password('faculty123'),
            role='faculty'
        )
        await faculty.insert()
        print('? Default faculty created: faculty@proxm.io / faculty123')
    else:
        print(f'? Found faculty user: {faculty.email}')

    existing_exams = await Exam.find({"title": {"$regex": "^Demo Exam"}}).to_list()
    if existing_exams:
        print('?? Demo exams already exist. Deleting them to recreate...')
        for ex in existing_exams:
            await ex.delete()

    print('?? Creating 3 Demo Exams...')

    exam1 = Exam(
        title='Demo Exam 1: Python Fundamentals',
        description='A basic exam covering Python fundamentals with MCQs and a simple coding question.',
        created_by=faculty.id,
        is_published=True,
        start_time=datetime.utcnow() - timedelta(days=1),
        end_time=datetime.utcnow() + timedelta(days=30),
        shuffle_questions=True,
        sections=[
            Section(
                title='Python Basics',
                description='Multiple choice questions on basic syntax.',
                time_limit_minutes=15,
                questions=[
                    Question(
                        question_text='Which of the following is a mutable data type in Python?',
                        question_type='mcq',
                        options=[
                            {'text': 'Tuple', 'is_correct': False},
                            {'text': 'List', 'is_correct': True},
                            {'text': 'String', 'is_correct': False},
                            {'text': 'Integer', 'is_correct': False},
                        ],
                        marks=1,
                        time_limit_seconds=60
                    ),
                    Question(
                        question_text='What is the output of print(2 ** 3)?',
                        question_type='mcq',
                        options=[
                            {'text': '6', 'is_correct': False},
                            {'text': '8', 'is_correct': True},
                            {'text': '9', 'is_correct': False},
                            {'text': 'Error', 'is_correct': False},
                        ],
                        marks=1,
                        time_limit_seconds=60
                    )
                ]
            ),
            Section(
                title='Basic Coding',
                description='Simple programming task.',
                time_limit_minutes=30,
                questions=[
                    Question(
                        question_text='Write a function dd(a, b) that returns the sum of two numbers.',
                        question_type='coding',
                        language='python',
                        starter_code='def add(a, b):\n    pass',                        test_wrapper='''import sys
data = sys.stdin.read().split()
if len(data) >= 2:
    print(add(int(data[0]), int(data[1])))''',
                        test_cases=[
                            {'input': '2 3', 'expected_output': '5', 'is_hidden': False},
                            {'input': '-1 1', 'expected_output': '0', 'is_hidden': False},
                            {'input': '10 20', 'expected_output': '30', 'is_hidden': True},
                        ],
                        marks=5,
                        time_limit_seconds=300
                    )
                ]
            )
        ]
    )

    exam2 = Exam(
        title='Demo Exam 2: Data Structures',
        description='An intermediate exam focusing on common data structures.',
        created_by=faculty.id,
        is_published=True,
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(days=7),
        sections=[
            Section(
                title='Theory',
                questions=[
                    Question(
                        question_text='Which data structure uses LIFO?',
                        question_type='mcq',
                        options=[
                            {'text': 'Queue', 'is_correct': False},
                            {'text': 'Stack', 'is_correct': True},
                            {'text': 'Linked List', 'is_correct': False},
                            {'text': 'Tree', 'is_correct': False},
                        ]
                    )
                ]
            ),
            Section(
                title='Implementation',
                questions=[
                    Question(
                        question_text='Implement a stack using a list.',
                        question_type='coding',
                        language='python',
                        starter_code='def push(stack, item):\n    pass',
                        test_cases=[
                            {'input': '[], 1', 'expected_output': '[1]', 'is_hidden': False},
                            {'input': '[1, 2], 3', 'expected_output': '[1, 2, 3]', 'is_hidden': True},
                        ],
                        marks=10
                    )
                ]
            )
        ]
    )

    exam3 = Exam(
        title='Demo Exam 3: Web Technologies',
        description='A quiz on HTML, CSS, and JS basics.',
        created_by=faculty.id,
        is_published=False,
        sections=[
            Section(
                title='Frontend Basics',
                questions=[
                    Question(
                        question_text='What does HTML stand for?',
                        question_type='mcq',
                        options=[
                            {'text': 'Hyper Text Markup Language', 'is_correct': True},
                            {'text': 'Home Tool Markup Language', 'is_correct': False},
                            {'text': 'Hyperlinks and Text Markup Language', 'is_correct': False},
                        ]
                    ),
                    Question(
                        question_text='Which property is used to change the background color?',
                        question_type='mcq',
                        options=[
                            {'text': 'color', 'is_correct': False},
                            {'text': 'bgcolor', 'is_correct': False},
                            {'text': 'background-color', 'is_correct': True},
                        ]
                    )
                ]
            )
        ]
    )

    await exam1.insert()
    await exam2.insert()
    await exam3.insert()

    print('? Successfully added 3 demo exams!')

if __name__ == '__main__':
    asyncio.run(main())


