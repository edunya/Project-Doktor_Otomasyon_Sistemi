#CREATE DATABASE doktor_otomasyon;
USE doktor_otomasyon;

CREATE TABLE Brans (
    BransID INT PRIMARY KEY AUTO_INCREMENT,
    Ad VARCHAR(100) NOT NULL
);

CREATE TABLE Doktor (
    DoktorID INT PRIMARY KEY AUTO_INCREMENT,
    Ad VARCHAR(50),
    Soyad VARCHAR(50),
    Telefon VARCHAR(15),
    Email VARCHAR(100),
    Sifre VARCHAR(100),
    BransID INT,
    FOREIGN KEY (BransID) REFERENCES Brans(BransID)
);

CREATE TABLE Hasta (
    HastaID INT PRIMARY KEY AUTO_INCREMENT,
    Ad VARCHAR(50),
    Soyad VARCHAR(50),
    TC CHAR(11) UNIQUE,
    Telefon VARCHAR(15),
    DogumTarihi DATE,
    Sifre VARCHAR(100)
);

CREATE TABLE Randevu (
    RandevuID INT PRIMARY KEY AUTO_INCREMENT,
    HastaID INT,
    DoktorID INT,
    Tarih DATETIME,
    Sikayet TEXT,
    FOREIGN KEY (HastaID) REFERENCES Hasta(HastaID),
    FOREIGN KEY (DoktorID) REFERENCES Doktor(DoktorID)
);

CREATE TABLE Muayene (
    MuayeneID INT PRIMARY KEY AUTO_INCREMENT,
    RandevuID INT UNIQUE,
    Teshis TEXT,
    Ilac TEXT,
    Notlar TEXT,
    FOREIGN KEY (RandevuID) REFERENCES Randevu(RandevuID)
);

CREATE VIEW AktifRandevular AS
SELECT r.RandevuID, h.Ad AS HastaAd, h.Soyad AS HastaSoyad, d.Ad AS DoktorAd, d.Soyad AS DoktorSoyad, r.Tarih
FROM Randevu r
JOIN Hasta h ON r.HastaID = h.HastaID
JOIN Doktor d ON r.DoktorID = d.DoktorID
WHERE r.Tarih > NOW();

CREATE INDEX idx_randevu_tarih ON Randevu(Tarih);

DELIMITER $$

CREATE TRIGGER trg_hasta_sil AFTER DELETE ON Hasta
FOR EACH ROW
BEGIN
    DELETE FROM Randevu WHERE HastaID = OLD.HastaID;
END$$

DELIMITER ;

INSERT INTO Brans (Ad) VALUES
('Dahiliye'),
('Kardiyoloji'),
('Nöroloji');

INSERT INTO Doktor (Ad, Soyad, Telefon, Email, Sifre, BransID) VALUES
('Ahmet', 'Yılmaz', '05001112233', 'ahmet@ornek.com', '1234', 1),
('Elif', 'Kaya', '05002223344', 'elif@ornek.com', '1234', 2),
('Mehmet', 'Demir', '05003334455', 'mehmet@ornek.com', '1234', 3);

INSERT INTO Hasta (Ad, Soyad, TC, Telefon, DogumTarihi, Sifre) VALUES
('Ali', 'Vural', '12345678901', '05001112233', '1995-06-15', '1234'),
('Ayşe', 'Arslan', '23456789012', '05002223344', '1992-03-10', '1234');

INSERT INTO Randevu (HastaID, DoktorID, Tarih, Sikayet) VALUES
(1, 1, '2025-05-21 10:00:00', 'Baş ağrısı'),
(2, 2, '2025-05-22 14:30:00', 'Göğüs ağrısı');

INSERT INTO Muayene (RandevuID, Teshis, Ilac, Notlar) VALUES
(1, 'Migren', 'Parol', 'Bol su içmesi önerildi.'),
(2, 'Kalp ritim bozukluğu', 'Beloc Zok', 'EKG kontrolü önerildi.');

ALTER TABLE Randevu ADD MuayeneDurumu BOOLEAN DEFAULT 0;
