#Mirror automagica Portal

## Usage

The base path for API will be /api

### Register and setup a machine, make it a bot

**Definition**

`POST /bot/setup`

***headers***

```json 
    {
        "user_secret": "User secret"
    }
```

***JSON Data***

```json 
    {
        "name": "Hostname or machine name"
    }
```

**Responses**

- `200 OK` on success
    ```json 
        {
            "bot_secret": "Bot secret"
        }
    ```
- `404 Not found` on error
    ```json 
        {
            "message": "Invalid login"
        }
    ```

### Indicate than a bot is alive (executed every 30 seconds)

**Definition**

`POST /bot/alive`

***headers***

```json
    {
        "bot_secret": "Bot secret, generated and retrieved by /setup resource"
    }
```

**Responses**

- `200 OK` on success
    ```json 
        {
            "success": "alive received"
        }
    ```
- `404 Not Found` on error
    ```json 
        {
            "error": "bot not found"
        }
    ```

### Next Job to execute (executed every 10 seconds)

**Definition**

`GET /job/next`

***headers***

```json
    {
        "bot_secret": "Bot secret, generated and retrieved by /setup resource"
    }
```

**Responses**

- `200 OK` on success
    ```json 
        {
            "job_id": "47bcd665-f97d-4976-82f9-2236e938de01",
            "parameters": "",
            "script_id": "3401cb43-05cf-46af-970c-3833fc854377",
            "script_version_id": "1ca42883-0f38-42d1-811f-8a43a285d21c"
        }
    ```
- `404 Not Found` on error
    ```json 
        {
            "error": "bot not found"
        }
    ```

### Gets script content

**Definition**

`GET /script`

***headers***

```json
    {
        "script_id": "Script id that is retrieved with /next resource",
        "script_version_id": "Script version id that is retrieved with /next resource",
        "bot_secret": "Bot secret, generated and retrieved by /setup resource"
    }
```

**Responses**

- `200 OK` on success
    ```json 
    {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Automagica Example Script"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# This imports all building blocks from Automagica so you can use them!\n",
                    "from automagica import *"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": null,
                "metadata": {},
                "outputs": [],
                "source": []
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [
                    {
                        "data": {
                            "text/plain": [
                                "'pass'"
                            ]
                        },
                        "execution_count": 2,
                        "metadata": {},
                        "output_type": "execute_result"
                    }
                ],
                "source": [
                    "# Make a window pop-up ask for user password\n",
                    "ask_user_password()\n",
                    "# Type in password and press 'submit', e.g. 'Sample password'\n"
                ]
            }
        ],
        "metadata":
            {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.7.5"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    ```
- `500 Internal Server Error` on error

### Retrieve details about upload the script execution evidence

**Definition**

`POST /job`

***headers***

```json
    {
        "bot_secret": "Bot secret, generated and retrieved by /setup resource",
        "job_id": "Process id or job id that bot machine has to execute",
        "job_status": "Job execution status",
		"job_error": "Error, only if it occurs when executing Jupyter notebook"
    }
```

**Responses**

- `200 OK` on success
    ```json 
        {
            "fields": {
                "job_id": "the job id",
                "extension": "ipynb"
            },
            "url": "http://localhost:5000/api/job/evidence"
        }
    ```
- `500 Internal Server Error` on error

### Retrieve details about service to consume to upload error evidence, if it occurs

**Definition**

`POST /job/screenshot`

***headers***

```json
    {
        "bot_secret": "Bot secret, generated and retrieved by /setup resource",
        "job_id": "Process id or job id that bot machine has to execute",
        "job_status": "Job execution status",
		"job_error": "Error, only if it occurs when executing Jupyter notebook"
    }
```

**Responses**

- `200 OK` on success
    ```json 
        {
            "fields": {
                "job_id": "the job id",
                "extension": "png"
            },
            "url": "http://localhost:5000/api/job/printscreen"
        }
    ```
- `500 Internal Server Error` on error

### Upload job executed evidence 

**Definition**

`POST /job/evidence`

***data***

```json 
{
    "job_id": "the job id",
    "extension": "ipynb",
    "file":"el archivo de Jupyter Notebook"
}
```

**Responses**

- `200 OK ` on success
    ```json
    {
        "message":"job evidence received"
    }
    ```

### Upload job executed errors, when they occur 

**Definition**

`POST /job/printsreen`

***data***

```json 
{
    "job_id": "the job id",
    "extension": "png",
    "file":"la imagen con los errores"
}
```

**Responses**

- `200 OK ` on success
    ```json
    {
        "message":"job evidence received"
    }
    ```