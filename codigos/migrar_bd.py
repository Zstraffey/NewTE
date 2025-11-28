import bcrypt
import classes
import mysql.connector  # ou use seu driver / classe bancoDados

def migrate():
    db = classes.bancoDados().conectar()
    cursor = db.cursor()

    # Assumindo que a coluna senha atualmente contém texto plano.
    cursor.execute("SELECT id_user, senha FROM usuario")
    rows = cursor.fetchall()

    for user_id, senha in rows:
        # detectar se já está em bcrypt (começa com $2b$ ou $2a$ etc.)
        if senha is None:
            continue
        if isinstance(senha, bytes):
            s = senha.decode("utf-8", errors="ignore")
        else:
            s = str(senha)

        if s.startswith("$2a$") or s.startswith("$2b$") or s.startswith("$2y$"):
            print(f"user {user_id} já está com hash. pulando.")
            continue

        # hash e update
        senha_hash = bcrypt.hashpw(s.encode("utf-8"), bcrypt.gensalt())
        cursor.execute("UPDATE usuario SET senha = %s WHERE id_user = %s", (senha_hash, user_id))
        print(f"Updated user {user_id}")

    db.commit()
    cursor.close()
    db.close()

if __name__ == "__main__":
    migrate()