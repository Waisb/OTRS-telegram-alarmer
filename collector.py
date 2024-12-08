from globals import TICKETS_DB_CONNECTION, TICKETS_DB_CURSOR, DB_LOCKER

def ticket_exist(ticket_num):
    with DB_LOCKER:
        TICKETS_DB_CURSOR.execute("SELECT * FROM Tickets WHERE Number = ?", (ticket_num,))
        ticketDataFromDB = TICKETS_DB_CURSOR.fetchall()
        if len(ticketDataFromDB) > 0:
            return True
        else:
            return False

def ticket_add(ticket_num, ticket_url):
    with DB_LOCKER:
        TICKETS_DB_CURSOR.execute("INSERT INTO Tickets (Number, Link) VALUES (?,?)", (ticket_num, ticket_url,))
        TICKETS_DB_CONNECTION.commit()
        
