from sqlalchemy.orm import Session
from database import get_db, Hospital
from schemas import HospitalResponse
from typing import Optional, List
import json

class HospitalService:
    def __init__(self):
        self.db = next(get_db())
    
    async def create_dummy_hospitals(self):
        """Create 20 dummy hospitals with specializations"""
        try:
            # Check if hospitals already exist
            existing_count = self.db.query(Hospital).count()
            if existing_count > 0:
                return
            
            dummy_hospitals = [
                {
                    "name": "MedCity General Hospital",
                    "location": "New York",
                    "address": "123 Medical Plaza, New York, NY 10001",
                    "phone_number": "+1-555-0101",
                    "email": "info@medcityny.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion", "radiofrequency_ablation"],
                    "available_slots": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
                },
                {
                    "name": "CardioCare Center",
                    "location": "Los Angeles",
                    "address": "456 Heart Street, Los Angeles, CA 90210",
                    "phone_number": "+1-555-0102",
                    "email": "contact@cardiocare.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion"],
                    "available_slots": ["08:00", "09:30", "11:00", "13:30", "15:00", "16:30"]
                },
                {
                    "name": "Advanced Heart Institute",
                    "location": "Chicago",
                    "address": "789 Cardiac Ave, Chicago, IL 60601",
                    "phone_number": "+1-555-0103",
                    "email": "info@advancedheart.com",
                    "specializations": ["interventional_cardiology", "radiofrequency_ablation"],
                    "available_slots": ["09:00", "10:30", "12:00", "14:00", "15:30", "17:00"]
                },
                {
                    "name": "Metro Cardiology Center",
                    "location": "Houston",
                    "address": "321 Pulse Drive, Houston, TX 77001",
                    "phone_number": "+1-555-0104",
                    "email": "appointments@metrocardio.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion", "radiofrequency_ablation"],
                    "available_slots": ["08:30", "10:00", "11:30", "14:30", "16:00"]
                },
                {
                    "name": "Phoenix Heart Specialists",
                    "location": "Phoenix",
                    "address": "654 Vascular Way, Phoenix, AZ 85001",
                    "phone_number": "+1-555-0105",
                    "email": "info@phoenixheart.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion"],
                    "available_slots": ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]
                },
                {
                    "name": "Boston Cardiac Center",
                    "location": "Boston",
                    "address": "987 Heart Lane, Boston, MA 02101",
                    "phone_number": "+1-555-0106",
                    "email": "contact@bostoncardiac.com",
                    "specializations": ["interventional_cardiology", "radiofrequency_ablation"],
                    "available_slots": ["08:00", "09:30", "11:00", "13:30", "15:00"]
                },
                {
                    "name": "Seattle Heart Institute",
                    "location": "Seattle",
                    "address": "147 Cardiac Blvd, Seattle, WA 98101",
                    "phone_number": "+1-555-0107",
                    "email": "info@seattleheart.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion", "radiofrequency_ablation"],
                    "available_slots": ["09:00", "10:30", "12:00", "14:00", "15:30", "17:00"]
                },
                {
                    "name": "Miami Vascular Center",
                    "location": "Miami",
                    "address": "258 Blood Flow St, Miami, FL 33101",
                    "phone_number": "+1-555-0108",
                    "email": "appointments@miamivascular.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion"],
                    "available_slots": ["08:30", "10:00", "11:30", "14:30", "16:00", "17:30"]
                },
                {
                    "name": "Denver Heart Clinic",
                    "location": "Denver",
                    "address": "369 Mountain View, Denver, CO 80201",
                    "phone_number": "+1-555-0109",
                    "email": "info@denverheart.com",
                    "specializations": ["interventional_cardiology", "radiofrequency_ablation"],
                    "available_slots": ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00"]
                },
                {
                    "name": "Atlanta Cardiac Specialists",
                    "location": "Atlanta",
                    "address": "741 Peach Tree Ave, Atlanta, GA 30301",
                    "phone_number": "+1-555-0110",
                    "email": "contact@atlantacardiac.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion", "radiofrequency_ablation"],
                    "available_slots": ["08:00", "09:30", "11:00", "13:30", "15:00", "16:30"]
                },
                {
                    "name": "Portland Heart Center",
                    "location": "Portland",
                    "address": "852 Rose City Dr, Portland, OR 97201",
                    "phone_number": "+1-555-0111",
                    "email": "info@portlandheart.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion"],
                    "available_slots": ["09:00", "10:30", "12:00", "14:00", "15:30"]
                },
                {
                    "name": "Nashville Cardiac Institute",
                    "location": "Nashville",
                    "address": "963 Music Row, Nashville, TN 37201",
                    "phone_number": "+1-555-0112",
                    "email": "appointments@nashvillecardiac.com",
                    "specializations": ["interventional_cardiology", "radiofrequency_ablation"],
                    "available_slots": ["08:30", "10:00", "11:30", "14:30", "16:00", "17:00"]
                },
                {
                    "name": "Las Vegas Heart Specialists",
                    "location": "Las Vegas",
                    "address": "159 Strip Blvd, Las Vegas, NV 89101",
                    "phone_number": "+1-555-0113",
                    "email": "info@vegasheart.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion", "radiofrequency_ablation"],
                    "available_slots": ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]
                },
                {
                    "name": "Minneapolis Vascular Center",
                    "location": "Minneapolis",
                    "address": "357 Twin Cities Ave, Minneapolis, MN 55401",
                    "phone_number": "+1-555-0114",
                    "email": "contact@minneapoliscardiac.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion"],
                    "available_slots": ["08:00", "09:30", "11:00", "13:30", "15:00", "16:30"]
                },
                {
                    "name": "Orlando Heart Institute",
                    "location": "Orlando",
                    "address": "741 Theme Park Dr, Orlando, FL 32801",
                    "phone_number": "+1-555-0115",
                    "email": "info@orlandoheart.com",
                    "specializations": ["interventional_cardiology", "radiofrequency_ablation"],
                    "available_slots": ["09:00", "10:30", "12:00", "14:00", "15:30", "17:00"]
                },
                {
                    "name": "San Diego Cardiac Center",
                    "location": "San Diego",
                    "address": "852 Pacific Coast Hwy, San Diego, CA 92101",
                    "phone_number": "+1-555-0116",
                    "email": "appointments@sandiegocardiac.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion", "radiofrequency_ablation"],
                    "available_slots": ["08:30", "10:00", "11:30", "14:30", "16:00"]
                },
                {
                    "name": "Detroit Heart Specialists",
                    "location": "Detroit",
                    "address": "963 Motor City Blvd, Detroit, MI 48201",
                    "phone_number": "+1-555-0117",
                    "email": "info@detroiheart.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion"],
                    "available_slots": ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00"]
                },
                {
                    "name": "Cleveland Cardiac Institute",
                    "location": "Cleveland",
                    "address": "147 Lake Erie Dr, Cleveland, OH 44101",
                    "phone_number": "+1-555-0118",
                    "email": "contact@clevelandcardiac.com",
                    "specializations": ["interventional_cardiology", "radiofrequency_ablation"],
                    "available_slots": ["08:00", "09:30", "11:00", "13:30", "15:00", "16:30"]
                },
                {
                    "name": "Pittsburgh Heart Center",
                    "location": "Pittsburgh",
                    "address": "258 Steel City Ave, Pittsburgh, PA 15201",
                    "phone_number": "+1-555-0119",
                    "email": "info@pittsburghheart.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion", "radiofrequency_ablation"],
                    "available_slots": ["09:00", "10:30", "12:00", "14:00", "15:30", "17:00"]
                },
                {
                    "name": "Tampa Bay Cardiac Specialists",
                    "location": "Tampa",
                    "address": "369 Gulf Coast Dr, Tampa, FL 33601",
                    "phone_number": "+1-555-0120",
                    "email": "appointments@tampabaycardiac.com",
                    "specializations": ["interventional_cardiology", "chronic_total_occlusion"],
                    "available_slots": ["08:30", "10:00", "11:30", "14:30", "16:00", "17:30"]
                }
            ]
            
            for hospital_data in dummy_hospitals:
                hospital = Hospital(
                    name=hospital_data["name"],
                    location=hospital_data["location"],
                    address=hospital_data["address"],
                    phone_number=hospital_data["phone_number"],
                    email=hospital_data["email"],
                    specializations=json.dumps(hospital_data["specializations"]),
                    available_slots=json.dumps(hospital_data["available_slots"])
                )
                self.db.add(hospital)
            
            self.db.commit()
            print("Created 20 dummy hospitals successfully!")
            
        except Exception as e:
            self.db.rollback()
            print(f"Error creating dummy hospitals: {e}")
            raise e
    
    async def get_hospitals(self, specialization: str = None, location: str = None) -> List[Hospital]:
        """Get hospitals with optional filtering"""
        query = self.db.query(Hospital)
        
        if specialization:
            query = query.filter(Hospital.specializations.contains(f'"{specialization}"'))
        
        if location:
            query = query.filter(Hospital.location.ilike(f"%{location}%"))
        
        return query.all()
    
    def get_hospital(self, hospital_id: int) -> Optional[Hospital]:
        """Get hospital by ID"""
        return self.db.query(Hospital).filter(Hospital.id == hospital_id).first()
    
    def create_hospital(self, hospital_data: dict) -> Hospital:
        """Create a new hospital (Admin function)"""
        try:
            hospital = Hospital(
                name=hospital_data["name"],
                location=hospital_data["location"],
                address=hospital_data["address"],
                phone_number=hospital_data["phone_number"],
                email=hospital_data["email"],
                specializations=json.dumps(hospital_data["specializations"]),
                available_slots=json.dumps(hospital_data["available_slots"])
            )
            
            self.db.add(hospital)
            self.db.commit()
            self.db.refresh(hospital)
            
            return hospital
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update_hospital(self, hospital_id: int, update_data: dict) -> Optional[Hospital]:
        """Update hospital information (Admin function)"""
        try:
            hospital = self.get_hospital(hospital_id)
            if not hospital:
                return None
            
            for key, value in update_data.items():
                if hasattr(hospital, key):
                    if key in ["specializations", "available_slots"]:
                        setattr(hospital, key, json.dumps(value))
                    else:
                        setattr(hospital, key, value)
            
            self.db.commit()
            self.db.refresh(hospital)
            return hospital
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_hospital(self, hospital_id: int) -> bool:
        """Delete hospital (Admin function)"""
        try:
            hospital = self.get_hospital(hospital_id)
            if not hospital:
                return False
            
            self.db.delete(hospital)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e


