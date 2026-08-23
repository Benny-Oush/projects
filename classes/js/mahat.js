class CompanyCar {
  constructor(licensePlate, manufacture, company) {
    this.licensePlate = licensePlate;
    this.manufacture = manufacture;
    this.company = company;
  }
  getLicensePlate = () => this.licensePlate;
  getManufacture = () => this.manufacture;
  getCompany = () => this.company
}

class CompanyLimit {
  constructor(companyName, limit) {
    this.companyName = companyName;
    this.limit = limit;
  }
  getCompanyName = () => this.companyName;
  getLimit = () => this.limit;
}

class Parking {
  constructor(cars=[], parkingSpots=[], currentCars = 0, limits=[]) {
    this.cars = cars;
    this.parkingSpots = parkingSpots;
    this.currentCars = currentCars;
    this.limits = limits;
  }
  checkSpot(spot) {
    for (const parkingSpot of this.parkingSpots) {
      if (spot === parkingSpot) {
        return false;
      }
    }
    return true;
  }
  parkCar(license, manufacture, company, spot) {
    if (!this.checkSpot(spot)) {
      console.log('Failure! Spot taken');
      return false;
      
    }
    if (this.currentCars >= 150) {
        console.log('Failure! The parking lot is full');
        return false
    }
    for (const limit of this.limits) {
        if (limit.companyName === company) {
            if (limit.limit === 0) {
                console.log('Failure! Company has reached it\'s limit');
                return false
            }
            limit.limit--
        }
    }
    this.cars.push(new CompanyCar(license, manufacture, company));
    this.currentCars++;
    this.parkingSpots.push(spot)
    console.log('Success!');
    return true;
  }
}

let parkingLot = new Parking()
parkingLot.limits.push(new CompanyLimit('google', 20))
parkingLot.parkCar('123', 'Reno', 'google', 'A1')
parkingLot.parkCar('567', 'Reno', 'google', 'A2')
console.log(parkingLot.limits.find((d) => d.getCompanyName() === 'google').getLimit());
// console.log(parkingLot.limits);

parkingLot.parkCar('890', 'Reno', 'google', 'A3')
parkingLot.parkCar('098', 'Reno', 'google', 'A4')
parkingLot.parkCar('321', 'Reno', 'google', 'A5')
parkingLot.parkCar('654', 'Reno', 'google', 'A6')

parkingLot.parkCar('783', 'Reno', 'google', 'A98')
parkingLot.parkCar('893', 'Reno', 'google', 'A8')
parkingLot.parkCar('234', 'Reno', 'google', 'A9')
parkingLot.parkCar('123', 'Reno', 'google', 'A7')
// console.log(parkingLot.limits);

parkingLot.parkCar('567', 'Reno', 'google', 'A21')
parkingLot.parkCar('890', 'Reno', 'google', 'A31')
parkingLot.parkCar('098', 'Reno', 'google', 'A41')
parkingLot.parkCar('321', 'Reno', 'google', 'A51')
parkingLot.parkCar('654', 'Reno', 'google', 'A61')
parkingLot.parkCar('783', 'Reno', 'google', 'A62')
parkingLot.parkCar('893', 'Reno', 'google', 'A81')
parkingLot.parkCar('234', 'Reno', 'google', 'A91')
parkingLot.parkCar('123', 'Reno', 'google', 'A12')
parkingLot.parkCar('567', 'Reno', 'google', 'A22')
parkingLot.parkCar('890', 'Reno', 'google', 'A32')

parkingLot.parkCar('098', 'Reno', 'google', 'A42')
parkingLot.parkCar('321', 'Reno', 'google', 'A52')
parkingLot.parkCar('654', 'Reno', 'google', 'A66')
parkingLot.parkCar('783', 'Reno', 'google', 'A65')
parkingLot.parkCar('893', 'Reno', 'google', 'A82')
parkingLot.parkCar('234', 'Reno', 'google', 'A92')

// console.log(parkingLot.limits);

