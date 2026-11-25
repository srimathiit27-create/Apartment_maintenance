package com.apartment.model;
public class Resident extends Entity<Integer> {
    private final String name, apartment, phone;
    private final int apartmentId;
    public Resident(int id,String name,int apartmentId,String apartment,String phone){super(id);this.name=name;this.apartmentId=apartmentId;this.apartment=apartment;this.phone=phone;}
    public Resident(int id,String name,String apartment,String phone){this(id,name,0,apartment,phone);}
    public String getName(){return name;} public String getApartment(){return apartment;} public String getPhone(){return phone;} public int getApartmentId(){return apartmentId;}
}
