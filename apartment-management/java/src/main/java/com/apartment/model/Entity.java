package com.apartment.model;
public abstract class Entity<ID> { private final ID id; protected Entity(ID id){this.id=id;} public ID getId(){return id;} }
