
// Utilisateurs administrateurs (dbOwner)
db.createUser({
  user: "owner1",
  pwd: "PasswordOwner1!",
  roles: [{ role: "dbOwner", db: "Medical_db" }]
});

db.createUser({
  user: "owner2",
  pwd: "PasswordOwner2!",
  roles: [{ role: "dbOwner", db: "Medical_db" }]
});

// Utilisateur avec rôle readWrite (script Python)
db.createUser({
  user: "migrateUser",
  pwd: "MigratePass123!",
  roles: [{ role: "readWrite", db: "Medical_db" }]
});

// Utilisateur en lecture seule (read)
db.createUser({
  user: "readOnlyUser",
  pwd: "ReadOnlyPass123!",
  roles: [{ role: "read", db: "Medical_db" }]
});