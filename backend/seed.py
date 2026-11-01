from datetime import time
from sqlalchemy import select
from database import SessionLocal
from models import Facility, Room, TimeSlot

CANONICAL_ROOMS = [
    ('Ruang Adi Soemarmo', 4), ('Ruang Balapan', 4), ('Ruang Jebres', 4),
    ('Ruang Tirtonadi', 6), ('Ruang Purwosari', 6), ('Ruang Solo Kota', 6),
    ('Ruang Batik Solo Trans', 8), ('Ruang Kerten', 8), ('Ruang Kleco', 8),
]
SLUGS = ['adi-soemarmo', 'balapan', 'jebres', 'tirtonadi', 'purwosari', 'solo-kota', 'batik-solo-trans', 'kerten', 'kleco']
DESCRIPTIONS = [
    'Ruang ringkas untuk belajar bersama dan diskusi kelompok kecil dengan monitor pendukung.',
    'Tempat berdiskusi dalam kelompok kecil, dilengkapi whiteboard untuk merangkai ide.',
    'Workspace untuk kerja kelompok dan sesi fokus bersama hingga empat peserta.',
    'Ruang meeting untuk meninjau pekerjaan, menyusun rencana, dan presentasi kelompok.',
    'Ruang diskusi enam peserta dengan monitor dan whiteboard untuk kerja kolaboratif.',
    'Workspace untuk rapat komunitas, kelompok belajar, dan pertemuan tim kecil.',
    'Ruang kolaborasi delapan peserta dengan proyektor untuk presentasi dan berbagi gagasan.',
    'Ruang kerja kelompok yang mendukung diskusi, presentasi, dan perencanaan tim.',
    'Workspace delapan peserta untuk lokakarya kecil dan sesi kolaborasi bersama.',
]

def seed(db):
    for name in ['Wi-Fi', 'Monitor', 'Whiteboard', 'AC', 'Proyektor', 'Stopkontak']:
        if not db.scalar(select(Facility).where(Facility.name == name)):
            db.add(Facility(name=name))
    db.flush()
    facilities = {f.name: f for f in db.scalars(select(Facility))}
    for i, (name, capacity) in enumerate(CANONICAL_ROOMS):
        room = db.scalar(select(Room).where(Room.name == name))
        if room:
            if room.capacity != capacity:
                raise RuntimeError(f'Kapasitas bawaan {name} tidak sesuai; audit data sebelum seed.')
            continue  # Tidak menimpa perubahan deskripsi/fasilitas/status admin.
        names = ['Wi-Fi', 'AC', 'Stopkontak', 'Monitor' if i % 2 == 0 else 'Whiteboard']
        if capacity >= 6:
            names.append('Whiteboard' if i % 2 == 0 else 'Monitor')
        if capacity == 8:
            names.append('Proyektor')
        db.add(Room(name=name, capacity=capacity, description=DESCRIPTIONS[i],
                    thumbnail=f'/images/rooms/{SLUGS[i]}.webp', visual_variant=i,
                    facilities=[facilities[n] for n in names]))
    for i in range(5):
        slot = db.get(TimeSlot, i + 1)
        start, end = time(9 + i * 2), time(11 + i * 2)
        if slot and (slot.start_time != start or slot.end_time != end):
            raise RuntimeError('Slot tetap berbeda dari konfigurasi resmi.')
        if not slot:
            db.add(TimeSlot(id=i + 1, start_time=start, end_time=end))
    db.commit()

if __name__ == '__main__':
    with SessionLocal() as db:
        seed(db)
    print('Seed selesai: 9 ruang bawaan, 5 slot tetap, fasilitas. Kalender libur dikelola terpisah.')
