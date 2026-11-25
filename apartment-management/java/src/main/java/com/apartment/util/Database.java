package com.apartment.util;
import java.sql.*;
public final class Database { private Database(){} public static Connection connect()throws SQLException{String url=System.getenv().getOrDefault("DB_URL","jdbc:mariadb://localhost:3306/apartment_mgmt");String user=System.getenv().getOrDefault("DB_USER","root"),pass=System.getenv().getOrDefault("DB_PASSWORD","");return DriverManager.getConnection(url,user,pass);} }
