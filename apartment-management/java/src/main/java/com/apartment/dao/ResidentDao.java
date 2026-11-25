package com.apartment.dao;
import com.apartment.model.Resident; import java.sql.*; import java.util.*;
public class ResidentDao implements CrudDao<Resident,Integer> {
 private final Connection c; public ResidentDao(Connection c){this.c=c;}
 public Optional<Resident> findById(Integer id)throws SQLException {try(var p=c.prepareStatement("SELECT resident_id,full_name,apartment_id,apartment_no,phone FROM resident r JOIN apartment a USING(apartment_id) WHERE resident_id=?")){p.setInt(1,id);try(var rs=p.executeQuery()){return rs.next()?Optional.of(map(rs)):Optional.empty();}}}
 public List<Resident> findAll()throws SQLException {List<Resident> out=new ArrayList<>();try(var s=c.createStatement();var rs=s.executeQuery("SELECT resident_id,full_name,apartment_id,apartment_no,phone FROM resident r JOIN apartment a USING(apartment_id) ORDER BY resident_id LIMIT 100")){while(rs.next())out.add(map(rs));}return out;}
 private Resident map(ResultSet rs)throws SQLException{return new Resident(rs.getInt(1),rs.getString(2),rs.getInt(3),rs.getString(4),rs.getString(5));}
 public Resident save(Resident r)throws SQLException {if(r.getId()!=null&&r.getId()>0){try(var p=c.prepareStatement("UPDATE resident SET full_name=?,apartment_id=?,phone=? WHERE resident_id=?")){p.setString(1,r.getName());p.setInt(2,r.getApartmentId());p.setString(3,r.getPhone());p.setInt(4,r.getId());if(p.executeUpdate()==0)throw new SQLException("Resident not found");}return findById(r.getId()).orElseThrow();}try(var p=c.prepareStatement("INSERT INTO resident(full_name,apartment_id,phone) VALUES(?,?,?)",Statement.RETURN_GENERATED_KEYS)){p.setString(1,r.getName());p.setInt(2,r.getApartmentId());p.setString(3,r.getPhone());p.executeUpdate();try(var keys=p.getGeneratedKeys()){keys.next();return findById(keys.getInt(1)).orElseThrow();}}}
 public boolean delete(Integer id)throws SQLException {try(var p=c.prepareStatement("DELETE FROM resident WHERE resident_id=?")){p.setInt(1,id);return p.executeUpdate()==1;}}
}
