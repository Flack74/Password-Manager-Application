import string
import traceback
from cryptography.fernet import Fernet
import mysql.connector as connector


class connectMySQL:
    def __init__(self):
        self.host = "127.0.0.1"
        self.user = "root"
        self.password = "P@ssw0rd123!"  # Replace with your MySQL password
        self.port = 3306
        self.database = "password_db"
        self.my_connector = None
        self.my_cursor = None

        # Use the specified secure key for Fernet
        self.key = b'tbBS3pbhaLepJ_eKakY0ynXp-fe09-pmLCc7m_GTzeE='
        self.cipher_suite = Fernet(self.key)

    def connect(self):
        """
        Connect to MySQL Database.
        """
        try:
            self.my_connector = connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database
            )
            self.my_cursor = self.my_connector.cursor(dictionary=True, buffered=True)
            print("Connected to the database successfully.")
        except Exception as e:
            print("Error connecting to the database:")
            print(traceback.format_exc())

    def is_password_valid(self, password):
        """
        Check if the password starts with a character and not a number.
        """
        if not password or password[0] in string.digits:
            return False
        return True

    def encrypt_password(self, password):
        """
        Encrypt the password.
        """
        try:
            encrypted_password = self.cipher_suite.encrypt(password.encode())
            return encrypted_password.decode()  # Store encrypted password as string
        except Exception as e:
            print("Error encrypting the password:")
            print(traceback.format_exc())
            return None

    def decrypt_password(self, encrypted_password):
        """
        Decrypt the password.
        """
        try:
            decrypted_password = self.cipher_suite.decrypt(encrypted_password.encode()).decode()
            return decrypted_password
        except Exception as e:
            print("Error decrypting the password:")
            print(traceback.format_exc())
            return None

    def get_data(self, sql):
        """
        Common function to get data from database.
        """
        self.connect()
        try:
            self.my_cursor.execute(sql)
            result = self.my_cursor.fetchall()
            return result
        except Exception as e:
            print("Error fetching data:")
            print(traceback.format_exc())
            return None
        finally:
            if self.my_connector:
                self.my_cursor.close()
                self.my_connector.close()

    def update_data(self, sql):
        """
        Common function to update database.
        """
        self.connect()
        try:
            self.my_cursor.execute(sql)
            self.my_connector.commit()
        except Exception as e:
            self.my_connector.rollback()
            print("Error updating data:")
            print(traceback.format_exc())
            return e
        finally:
            if self.my_connector:
                self.my_cursor.close()
                self.my_connector.close()

    def create_login_account(self, user_name, password):
        """
        Insert new login account data with password validation.
        """
        if not self.is_password_valid(password):
            raise ValueError("Password must start with a character, not a number.")

        encrypted_password = self.encrypt_password(password)
        if encrypted_password:
            sql = f"INSERT INTO user_tb (user_name, password) VALUES ('{user_name}', '{encrypted_password}')"
            result = self.update_data(sql=sql)
            return result

    def check_username(self, username):
        """
        Check the username when creating a new login account.
        """
        sql = f"SELECT * FROM user_tb WHERE user_name='{username}'"
        result = self.get_data(sql=sql)
        return result

    def validate_login(self, user_name, password):
        """
        Validate the login credentials.
        """
        encrypted_password = self.encrypt_password(password)
        sql = f"SELECT * FROM user_tb WHERE user_name='{user_name}' AND password='{encrypted_password}'"
        result = self.get_data(sql=sql)
        return result

    def get_password_list(self, user_id, search_username, search_website):
        """
        Search and get password data from the database.
        """
        sql = f"""
            SELECT * FROM password_tb 
                WHERE user_id={user_id} 
                    AND user_name LIKE '%{search_username}%'
                    AND website LIKE '%{search_website}%';
        """
        result = self.get_data(sql=sql)
        if result:
            for row in result:
                row['password'] = self.decrypt_password(row['password'])
        return result

    def delete_password_data(self, id):
        """
        Delete selected password data from the database.
        """
        sql = f"DELETE FROM password_tb WHERE id={id}"
        result = self.update_data(sql=sql)
        return result

    def save_new_password(self, user_id, user_name, website, password):
        """
        Save the newly generated password data with encryption.
        """
        encrypted_password = self.encrypt_password(password)
        if encrypted_password:
            sql = f"""
                INSERT INTO password_tb (user_id, user_name, website, password)
                    VALUES ({user_id}, '{user_name}', '{website}', '{encrypted_password}');
            """
            result = self.update_data(sql=sql)
            return result

    def create_config_data(self, user_id,
                           lowercase="abcdefghijklmnopqrstuvwxyz",
                           uppercase="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                           numbers="1234567890",
                           special_characters="@#$%&^!"):
        """
        Create configuration data for a special account.
        """
        sql = f"""
            INSERT INTO configuration_tb (user_id, lowercase, uppercase, numbers, special_characters )
                VALUES ({user_id}, '{lowercase}', '{uppercase}', '{numbers}', '{special_characters}');
        """
        result = self.update_data(sql=sql)
        return result

    def check_config_data(self, user_id):
        """
        Check if the configuration data for the user is in the database.
        """
        sql = f"SELECT * FROM configuration_tb WHERE user_id={user_id}"
        result = self.get_data(sql=sql)
        return result

    def update_config_data(self, user_id, lowercase, uppercase, numbers, special_characters):
        """
        Update configuration data.
        """
        sql = f"""
            UPDATE configuration_tb 
                SET lowercase='{lowercase}', uppercase='{uppercase}',
                    numbers='{numbers}', special_characters='{special_characters}'
                WHERE user_id={user_id}
        """
        result = self.update_data(sql=sql)
        return result

    def test_encryption_decryption(self):
        """
        Test encryption and decryption methods.
        """
        try:
            original_password = "test_password"
            encrypted = self.encrypt_password(original_password)
            if encrypted:
                print(f"Encrypted password: {encrypted}")
                decrypted = self.decrypt_password(encrypted)
                if decrypted:
                    print(f"Decrypted password: {decrypted}")
                    assert original_password == decrypted, "Decryption failed"
                else:
                    print("Decryption returned None")
            else:
                print("Encryption returned None")
        except Exception as e:
            print("Error in encryption/decryption test:")
            print(traceback.format_exc())


# Example usage
if __name__ == "__main__":
    db = connectMySQL()
    db.connect()

    # Test encryption and decryption
    db.test_encryption_decryption()

    # Example operations
    try:
        db.create_login_account("test_user", "123password")  # This should raise an error
    except ValueError as e:
        print(f"Error: {str(e)}")

    try:
        db.create_login_account("test_user", "password123")  # This should also raise an error
    except ValueError as e:
        print(f"Error: {str(e)}")

    # Correct password
    db.create_login_account("test_user", "validpassword")
    print(db.check_username("test_user"))
