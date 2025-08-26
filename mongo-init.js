db.createUser({
  user: "adminuser1",
  pwd: "StrongAdminPass1!",
  roles: [ { role: "root", db: "admin" } ]
});

db.createUser({
  user: "adminuser2",
  pwd: "StrongAdminPass2!",
  roles: [ { role: "root", db: "admin" } ]
});

db = db.getSiblingDB('Medical_db');

db.createUser({
  user: "migrateUser",
  pwd: "MigratePass123!",
  roles: [ { role: "readWrite", db: "Medical_db" } ]
});

db.createUser({
  user: "readOnlyUser",
  pwd: "ReadOnlyPass123!",
  roles: [ { role: "read", db: "Medical_db" } ]
});