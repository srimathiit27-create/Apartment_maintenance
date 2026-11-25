package com.apartment.service;
import com.apartment.dao.ResidentDao; import com.apartment.model.Resident; import java.sql.*; import java.util.regex.Pattern;
public class ResidentService {
 private static final Pattern PHONE=Pattern.compile("^[6-9][0-9]{9}$"); private final Connection connection; private final ResidentDao dao;
 public ResidentService(Connection connection){this.connection=connection;this.dao=new ResidentDao(connection);}
 public Resident register(String name,int apartmentId,String phone)throws SQLException {
  if(name==null||name.isBlank())throw new ValidationException("Resident name is required");
  if(phone==null||!PHONE.matcher(phone).matches())throw new ValidationException("Enter a valid 10-digit mobile number");
  try(var p=connection.prepareStatement("SELECT occupancy_status FROM apartment WHERE apartment_id=?")){p.setInt(1,apartmentId);try(var rs=p.executeQuery()){if(!rs.next()||!rs.getString(1).equals("Occupied"))throw new ValidationException("Apartment must exist and be occupied");}}
  return dao.save(new Resident(0,name,apartmentId,"",phone));
 }
}
