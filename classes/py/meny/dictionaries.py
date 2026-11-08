# מילון התחלתי
college = {
    "Computer Science": {
        "Class A": [
            {
                "name": "David Levi",
                "grades": {"Programming": 85, "Data Structures": 90}
            },
            {
                "name": "Ruth Cohen",
                "grades": {"Programming": 78, "Data Structures": 92}
            }
        ],
        "Class B": [
            {
                "name": "Yossi Israeli",
                "grades": {"Programming": 88, "Data Structures": 84}
            }
        ]
    },
    "Engineering": {
        "Class C": [
            {
                "name": "Sarah Jacob",
                "grades": {"Mathematics": 95, "Physics": 90}
            },
            {
                "name": "Eitan Nachmani",
                "grades": {"Mathematics": 80, "Physics": 85}
            }
        ]
    }
}

def add_department(college: dict, department_name: str) -> None:
    if department_name not in college:
        college[department_name] = {}
        print("\nDepartment added successfully!")
        return
    print("\nDepartment already exists!")

def add_class(college: dict, department_name: str, class_name: str) -> None:
    if department_name not in college:
        print("\nError!\nValues not valid")
        return
    if class_name not in college[department_name]:
        college[department_name][class_name] = []
        print("\nClass added successfully!")
        return
    print("\nClass already exists!")

def add_student(college: dict, department_name: str, class_name: str, student_name: str, grades: dict) -> None:
    if department_name not in college or class_name not in college[department_name]:
        print("\nError!\nValues not valid")
        return
    college[department_name][class_name].append({"name": student_name, "grades": grades})
    print("\nStudent added successfully!")

def calculate_student_average(student: dict) -> float:
    if not student or not student["grades"]:
        return 0.0
    total = 0
    for grade in student["grades"].values():
        total += grade
    return total/len(student["grades"])

def calculate_class_average(class_students: list) -> float:
    if not class_students:
        return 0.0
    total = 0
    for student in class_students:
        total += calculate_student_average(student)
    return total/len(class_students)

def calculate_department_average(department_classes: dict) -> float:
    if not department_classes:
        return 0.0
    total = 0
    count = 0
    for students_class in department_classes.values():
        if not students_class:
            continue
        for student in students_class:
            count += 1
            total += calculate_student_average(student)
    return total/count if count > 0 else 0.0

def get_student_grades() -> dict:
    result = {}
    while True:
        try:
            result[input("Enter subject: ")] = int(input("\nEnter grade: "))
            selection = input("\nDo you want to enter another grade? (y/n): ").lower()
            while selection not in ["y", "n"]:
                print("Error! Please enter 'y' or 'n'")
                selection = input("\nDo you want to enter another grade? (y/n): ").lower()
            if selection == "n":
                break
        except Exception as e:
            print("\nSomthing went wrong")
            print(f'Error: {e}')
    return result

def menu() -> None:
    def print_menu():
        print("\nWELCOME!\n")
        print("Enter 1 to add a department\nEnter 2 to add a class to a department\nEnter 3 to add a student to a class\nEnter 4 to calculate a student's average\nEnter 5 to calculate a class's average\nEnter 6 to calculate a department's average\nEnter 7 to exit")
    user_select = ""
    while user_select != "7":
        print_menu()
        try:
            user_select = input("\nEnter your selection: ")
            match user_select:
                case "1":
                    add_department(college, input("\nEnter the new department: "))
                case "2":
                    add_class(college, input("\nEnter the department's name: "), input("Enter the new class's name: "))
                case "3":
                    add_student(college, input("\nEnter the department's name: "), input("Enter the new class's name: "), input("Enter the student's name: "), get_student_grades())
                case "4":
                    students_class = college[input("\nEnter department: ")][input("Enter the class name: ")]
                    student_name = input("Enter the student's name: ")
                    found = False
                    for student in students_class:
                        if student["name"] == student_name:
                            found = True
                            print(f"\nAverage: {calculate_student_average(student)}")
                            break
                    if not found:
                        print("\nNo such student in this class")
                case "5":
                    students_class = college[input("\nEnter department: ")][input("Enter the class name: ")]
                    print(calculate_class_average(students_class))
                case "6":
                    department = college[input("\nEnter department: ")]
                    print(calculate_department_average(department))
                case "7":
                    user_select = "7"
                case _:
                    raise Exception('Please enter a valid selection')
        except Exception as e:
            print("\nSomething went wrong")
            print(f'Error: {e}')
    print("\nExiting...")

menu()