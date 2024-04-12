This documentation was heavily inspired by [this](https://gist.github.com/azagniotov/a4b16faf0febd12efbc6c3d7370383a6) example of creating a swagger-like API documentation with Markdown.

# Authentication
#### Users need a user token to interact with most of the API. To create one they'll have to create a user in the website. Then they can get their user token with the following endpoint.
<details>
    <summary>
        <code>POST</code> <code><b>/api/get-user-token/</b></code> <code>(gets user credentials and returns user token)</code>
    </summary>

#### Authentication
   > Not required

#### Parameters
   > | Name       | Type     | Data Type | Description         |
   > |------------|----------|-----------|---------------------|
   > | `username` | required | string    | The user's username |
   > | `password` | required | string    | The user's password |

#### Responses
   > |  HTTP Code  | Content-Type       | Response             |
   > |-------------|--------------------|----------------------|
   > | `200`       | `application/json` | `{"token": <token>}` |

#### Example cURL
   > TODO!
</details>

# Scientist

<details>
    <summary>
        <code>GET</code> <code><b>/api/scientist/</b></code> <code>(gets all scientists)</code>
    </summary>

#### Authentication
   > Required

#### Parameters
   > None

#### Responses
   > |  HTTP Code  | Content-Type       | Response                                       |
   > |-------------|--------------------|------------------------------------------------|
   > | `200`       | `application/json` | `JSON String with all scientists' information` |

#### Example cURL
   > TODO!
</details>

<details>
    <summary>
        <code>POST</code> <code><b>/api/scientist/</b></code> <code>(creates a scientist)</code>
    </summary>

#### Authentication
   > Required

#### Parameters
   > | Name         | Type     | Data Type | Description                |
   > |--------------|----------|-----------|----------------------------|
   > | `first_name` | required | string    | The scientist's first name |
   > | `last_name`  | required | string    | The scientist's last name  |
   > | `email`      | required | string    | The scientist's email      |
   > | `ci`         | required | string    | The scientist's ci         |

#### Responses
   > |  HTTP Code  | Content-Type       | Response                                                   |
   > |-------------|--------------------|------------------------------------------------------------|
   > | `201`       | `application/json` | `JSON String with all the created scientist's information` |

#### Example cURL
   > TODO!
</details>

<details>
    <summary>
        <code>GET</code> <code><b>/api/scientist/{id}/</b></code> <code>(gets scientist with {id} as a primary key)</code>
    </summary>

#### Authentication
   > Required

#### Parameters
   > | Name | Type     | Data Type | Description        |
   > |------|----------|-----------|--------------------|
   > | `id` | required | string    | The scientist's id |

#### Responses
   > |  HTTP Code  | Content-Type       | Response                                                 |
   > |-------------|--------------------|----------------------------------------------------------|
   > | `201`       | `application/json` | `JSON String with the requested scientist's information` |

#### Example cURL
   > TODO!
</details>

<details>
    <summary>
        <code>PUT</code> <code><b>/api/scientist/{id}/</b></code> <code>(edit scientist with {id} as a primary key)</code>
    </summary>

#### Authentication
   > Required

#### Parameters
   > | Name         | Type     | Data Type | Description                |
   > |--------------|----------|-----------|----------------------------|
   > | `first_name` | optional | string    | The scientist's first name |
   > | `last_name`  | optional | string    | The scientist's last name  |
   > | `email`      | optional | string    | The scientist's email      |
   > | `ci`         | optional | string    | The scientist's ci         |

#### Responses
   > |  HTTP Code  | Content-Type       | Response                                         |
   > |-------------|--------------------|--------------------------------------------------|
   > | `200`       | `application/json` | `{"message": "Scientist updated successfully!"}` |

#### Example cURL
   > TODO!
</details>

<details>
    <summary>
        <code>DELETE</code> <code><b>/api/scientist/{id}/</b></code> <code>(delete scientist with {id} as a primary key)</code>
    </summary>

#### Authentication
   > Required

#### Parameters
   > None

#### Responses
   > |  HTTP Code  | Content-Type       | Response                                         |
   > |-------------|--------------------|--------------------------------------------------|
   > | `200`       | `application/json` | `{'message': 'Scientist deleted successfully!'}` |

#### Example cURL
   > TODO!
</details>
