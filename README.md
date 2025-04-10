![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
[![Machine Learning Client CI](https://github.com/software-students-spring2025/4-containers-byteme/actions/workflows/ml-client.yml/badge.svg?branch=main)](https://github.com/software-students-spring2025/4-containers-byteme/actions/workflows/ml-client.yml)
[![Web App Client CI](https://github.com/software-students-spring2025/4-containers-byteme/actions/workflows/web-app.yml/badge.svg?branch=main)](https://github.com/software-students-spring2025/4-containers-byteme/actions/workflows/web-app.yml)

# FeelWrite

## Project Overview

FeelWrite is a responsive digital journal web app that allows users to log their daily experiences and receive immediate feedback based on the sentiment of their entries. Users can type journal entries on the website, and the application uses Machine Learning to analyze the sentiment of the text, determining whether the user is in a positive, negative, or neutral emotional state. Based on the analysis of each entry, the website generates a personalized response, such as providing a motivational or empathetic message with a background image tailored to the user's mood. It also displays a mood meter bar corresponding to the sentiment score of the user's journal entry (5 = the most positive mood, 1 = the most negative mood). In addition, users can also view their previous entries, allowing them to track and reflect on their emotional journey.

## Teammates

- [Siyu Lei](https://github.com/em815)
- [Jessica Chen](https://github.com/jessicahc)
- [Shayne Chan](https://github.com/shayne773)
- [Lina Sanchez](https://github.com/linahsan)

## Instructions to Set Up and Run the Project

1. **Clone this repository to your local machine:**

```sh
git clone https://github.com/software-students-spring2025/4-containers-byteme.git
```

2. **Set up environment variables:**

- In your cloned project directory, go to the `machine-learning-client` directory:

```sh
cd 4-containers-byteme/machine-learning-client
```

- Copy the `env.example` file and rename it to `.env`:

```sh
cp env.example .env
```

- Repeat the same process to create another `.env` under the `web-app` directory:

```sh
cd ../web-app
cp env.example .env
```

3. **Install and run Docker Desktop:**

- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- After installation, make sure Docker Desktop is running.
- Create a [Docker Hub](https://hub.docker.com/) account if you don’t have one already.

4. **Run the Docker containers**:

- Make sure you’re in the top-level project directory where the `docker-compose.yml` file is located.
- Use Docker Compose to boot up the web app, machine learning client, and mongodb database:

```sh
docker compose up --force-recreate --build
```

5. **Access the web app:**

- Open a web browser and go to [http://localhost:5001](http://localhost:5001) to view and interact with our app.

6. **Stop the containers:**

- When you are done viewing our web app, run the following command in a separate terminal window to stop the containers:

```sh
docker compose down
```
