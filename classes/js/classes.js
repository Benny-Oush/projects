class Bottle {
  constructor(size) {
    this.size = size;
    this.amount =  0;
  }
  add(amountToAdd) {
    const total = (this.amount += amountToAdd);
    if (total > this.size) {
      console.log(`${total - this.size} litters was spilled!`);
      this.amount = this.size;
      return;
    }
    this.amount = total;
  }
  spill(amountToSpill) {
    let spilled
    if (amountToSpill > this.amount) {
      console.log(`Spilled only ${this.amount} (instead of ${amountToSpill})`);
      spilled = this.amount
      this.amount = 0;
      return spilled
    }
    spilled = this.amount -= amountToSpill
    this.amount -= amountToSpill;
    return spilled
  }
  pour(otherBottle, amountToPour) {
    console.log(
      `Before:\n Bottle: ${this.amount}\n Other bottle: ${otherBottle.amount}`,
    );
    otherBottle.add(this.spill(amountToPour));
    console.log(
      `After:\n Bottle: ${this.amount}\n Other bottle: ${otherBottle.amount}`,
    );
  }
}

const bottle1 = new Bottle(2);
bottle1.add(1)
const bottle2 = new Bottle(3);
bottle2.add(2)
bottle2.spill(3)
bottle1.pour(bottle2, 2);
