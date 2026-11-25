package com.apartment.dao;
import com.apartment.model.Entity; import java.sql.SQLException; import java.util.*;
public interface CrudDao<T extends Entity<ID>,ID>{ Optional<T> findById(ID id)throws SQLException; List<T> findAll()throws SQLException; T save(T value)throws SQLException; boolean delete(ID id)throws SQLException; }
