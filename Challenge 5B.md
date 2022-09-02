## PALINDROME's Secret

We are given a website and its source code. There is a login page. 

![Login Page](./Images/Challenge5_1.png)

```js
const postLoginHandler = async (req, res) => {
    const { email, password } = req.body
    if (!email || !password)
        return res.status(400).send({ message: 'Missing email or password' })

    const rows = await query(`SELECT * FROM users WHERE email = ? AND password = ?`, [email, password])
    if (rows.length === 0)
        return res.status(401).send({ message: 'Invalid email or password' })

    req.session.userId = rows[0].id
    return res.status(200).send({ message: "Success" })
}
```

This is the login handler. We can use the exploit [here](https://flattsecurity.medium.com/finding-an-unseen-sql-injection-by-bypassing-escape-functions-in-mysqljs-mysql-90b27f6542b4) to perform sql injection and obtain a login token.

```json
{
    "email":{
        "email": 1
    },
    "password":{
        "password": 1
    }
}
```
![Login Success](./Images/Challenge5_2.png)

We use burpsuite to intercept the request, change the json object that is POST-ed and then we can login into the portal!

![Login Success GUI](./Images/Challenge5_3.png)

The only place the admin token is present is in the middleware. It seems like we need the connection to originate from localhost. Probably means we need to find some place to conduct an SSRF attack.

```js
const authenticationMiddleware = async (req, res, next) => {
    if (req.session.userId) {
        if (req.ip === '127.0.0.1')
            req.session.token = process.env.ADMIN_TOKEN 

        next()
    }
    else 
        return res.redirect('/login')
}
```

The place with the highest chance of SSRF looks like the `report-issue` feature, where we can input an URL to the server to scan. However to get to the `do-report` feature, we are blocked by the proxy. The `do-report` path is mapped to `forbidden`, instead of `do-report`.

```
map             /login          http://app:8000/login
map             /index          http://app:8000/index
map             /token          http://app:8000/token
map             /verify         http://app:8000/verify
map             /report-issue   http://app:8000/report-issue
map             /static         http://app:8000/static
map             /do-report      http://app:8000/forbidden
regex_redirect  http://(.*)/    http://$1/index
```

It seems like the proxy used is `Trafficserver 9.1.0`. This seems to be an old version of Apache Traffic Server.

```
RUN curl -L https://archive.apache.org/dist/trafficserver/trafficserver-9.1.0.tar.bz2 > ats.tar.bz2 && \
    tar xf ats.tar.bz2 && \
    cd trafficserver-9.1.0 && \
    ./configure --prefix=/opt/ts && \
    make && \
    make install
```

