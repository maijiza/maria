#!/usr/bin/env python3
"""
Test script per verificare la connessione a Neo4j
"""

from neo4j import GraphDatabase
import json

def test_neo4j_connection():
    """Test della connessione a Neo4j"""
    
    # Configurazione Neo4j
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "graphiti_password_2024"
    
    print("🔍 Testing Neo4j Connection...")
    print(f"URI: {uri}")
    print(f"Username: {username}")
    
    try:
        # Connessione
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            # Test query semplice
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            
            if record:
                print(f"✅ Connection successful!")
                print(f"Message: {record['message']}")
                
                # Test informazioni database
                result = session.run("CALL dbms.components() YIELD name, versions, edition")
                for record in result:
                    print(f"📊 Component: {record['name']} - Version: {record['versions'][0]} - Edition: {record['edition']}")
                
                # Test creazione nodo
                result = session.run("CREATE (n:TestNode {message: 'Graphiti Docker Test', timestamp: datetime()}) RETURN n")
                record = result.single()
                
                if record:
                    print("✅ Test node created successfully!")
                    
                    # Count nodes
                    result = session.run("MATCH (n) RETURN count(n) as total_nodes")
                    record = result.single()
                    print(f"📊 Total nodes in database: {record['total_nodes']}")
                
                return True
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    finally:
        if 'driver' in locals():
            driver.close()

if __name__ == "__main__":
    success = test_neo4j_connection()
    if success:
        print("\n🎉 Neo4j test completed successfully!")
    else:
        print("\n💥 Neo4j test failed!")
