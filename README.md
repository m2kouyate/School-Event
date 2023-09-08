# School Event Registrations

## Objective

The objective of this project was to develop a web application using the Django Python web framework to create an event registration system for a school's extracurricular activities.

## Features

### Event Information
- **Event Name**: The name of the event.
- **Event Date and Time**: The date and time the event is scheduled to take place.
- **Event Location**: The location where the event will be held.
- **Event Description**: A detailed description of the event.
- **Maximum Number of Participants**: The maximum number of participants allowed for the event.

### Participant Registration
- **Registration Feature**: Users can register for events by providing necessary details.
- **User Details**: Including First Name, Last Name, Profile Picture (optional, with a default placeholder image), Email Address (unique), and Phone Number.

### Filtering and Display
- **Event Filtering**: Users can filter events based on their type or date.
- **Event List**: A list displaying event names, dates, and locations. Initially, only current events are displayed with an option to view past events.

### Event Details
- **Detailed View**: Clicking on an event's name leads to a detailed page displaying all the information about the event, including images. Event creators can see options to edit or delete the event, as well as a list of participants.

### Event Types (Superuser Only)
- **Event Type Creation and Management**: Superusers can create, view, update, and delete event types.

### Importer
- **Security**: Only logged-in users can access and use the importer.
- **Functionality**: Allows bulk addition of event details to the system through CSV files, handling event details and image filenames.
- **Image Handling**: In case images are missing, events will be displayed without an images.
- **Event Type Selection**: Users have an option to select the type of events being imported (not mandatory).

### Database and Backend
- **Database**: The application uses SQLite as the database backend.
- **Framework**: Developed using the Django Python web framework.

### Authentication
- **Superuser**: Only superusers have the authority to manage event types.
- **User Authentication**: Implemented to secure access to the importer and other functionalities.

## Installation

1. Clone the repository: `git clone https://github.com/m2kouyate/School-Event.git`
2. Navigate to the project directory: `cd school_event_registration`
3. Install the necessary dependencies: `pip install -r requirements.txt`


## Running the Application
1. Create a superuser: `python3 manage.py createsuperuser`
2. Apply the migrations: `python3 manage.py migrate`
3. Run the server: `python3 manage.py runserver`
4. Access the application at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Usage

- **Event Type Management**: Superusers can manage event types through the dedicated section.
- **Event Creation**: Create events by navigating to the event creation page. 
- **Importer**: Accessible to logged-in users for bulk addition of event details.
- **Participant Registration**: Register for events through the event details page.


