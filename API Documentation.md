

# API Documentation

Below is the documentation for the UWHvZ API. Endpoints will be added, and this document is subject to be expanded upon. 

\* = requires authentication, and two cookies named `sessionid` and `csrftoken`.

## Login

`/api/v1/auth/login/`

#### Method

`POST`

#### Body parameters

- `username`: email address of the account
- `password`: password of the account.

#### Success Response

`Success`

Authenticates the user with the associated username. Attaches two cookies with names `sessionid` and `csrftoken` which identify the user sessions.

#### Failure Response

`403` - Login failure, incorrect credentials.

## Logout*

`/api/v1/auth/logout/`

#### Method

`GET`

#### Parameters

None

#### Body parameters

None

#### Success Response

`Success`

Refreshes `csrftoken` and removes `sessionid` cookie.

#### Failure Response

`Logout Failed`

This means you had invalid cookies.

## Account Information*

**Note**: This endpoint is currently only built for players. Moderator and spectator information collecting may be added later.

`/api/v1/account_info/`

#### Parameters

None

#### Body parameters

None

#### Success Response

Returns a JSON Object with the fields:

| Name         | Type                | Description                                                  |
| ------------ | ------------------- | ------------------------------------------------------------ |
| `code`       | String              | Player code as a string                                      |
| `roleChar`   | Char                | One character that represents the role of the player. `H` for human, `Z` for zombie, and `S` for spectators |
| `is_oz`      | Boolean             | Whether the player is an OZ                                  |
| `name`       | String              | Player's name                                                |
| `email`      | String              | Player's email                                               |
| `score`      | Integer             | Player's score                                               |
| `shop_score` | Integer             | Player's points available for use in the shop.               |
| `game`       | Game (see below)    | Game that this player is associated with. **Use this to check if the user is currently playing.** |
| `faction`    | Faction (see below) | Faction that the player is associated with.                  |

##### Game

| Name     | Type   | Description                                                  |
| -------- | ------ | ------------------------------------------------------------ |
| `name`   | String | Game name                                                    |
| `status` | String | This is the game status, and can be either `running`, `finished`, or `signups`. |
|  started\_on | String | Time that the current game started. Given in ISO8601. |
|  ended\_on | String | Time that the current game ended, in ISO8601 format. This field is null if the current game has not finished yet. |

##### Faction

| Name          | Type   | Description         |
| ------------- | ------ | ------------------- |
| `name`        | String | Name of faction     |
| `description` | String | Faction description |
| `modifiers`   | Array(Modifier, see below) | List of Modifiers that a faction gives. |

##### Modifier

| Name              | Type   | Description          |
| ----------------- | ------ | -----------          |
| `modifier_amount` | String | Quantity of modifier |
| `type`            | String | Type of modifier - `O` for one time use, `S` for supply codes, and `T` on tags. |

#### Failure Response

`Logout Failed`

This means you had invalid cookies
