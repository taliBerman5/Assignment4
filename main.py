from datetime import datetime
import sys
import Repository
import DTO

repo = Repository.repo


def parseConfig(path):
    file = open(path, "r")
    lines = file.readlines()
    quantity = lines.pop(0).replace('\n', '').split(",")
    quantity.reverse()
    lines.reverse()
    dto = [DTO.Logistic, DTO.Clinic, DTO.Supplier, DTO.Vaccine]
    dao = [repo.logistics, repo.clinics, repo.suppliers, repo.vaccines]
    for i in range(4):
        for j in range(int(quantity[i])):
            params = lines.pop(0).replace('\n', '').split(',')
            dao[i].insert(dto[i](*params))
    file.close()


def parseOrders(path):
    file = open(path, "r")
    lines = file.readlines()
    orders = []
    for line in lines:
        line.replace('\n', '')
        order = line.split(',')
        orders.append(order)
    file.close()
    return orders


def execOrder(order, file):
    if len(order) == 3:
        receive(order)
    else:
        send(order)
    updateOutput(file)


def send(order):
    city = order[0]
    amount = int(order[1])
    # update clinic demand
    clinic = repo.clinics.find(location=city)[0]
    repo.clinics.update({'demand': (clinic.demand - amount)}, {'location': city})
    # update count_sent
    logi = repo.logistics.find(id=clinic.logistic)[0]
    repo.logistics.update({'count_sent': (logi.count_sent + amount)}, {'id': logi.id})
    # update vaccine
    vaccines = repo.orderedVaccines()
    index = 0
    while amount > 0:
        vaccine = vaccines[index]
        amount_v = vaccine.quantity
        if amount >= amount_v:
            repo.vaccines.delete(id=vaccine.id)
        else:
            repo.vaccines.update({'quantity': amount_v - amount}, {'id': vaccine.id})

        amount = amount - amount_v
        index +=1


def receive(order):
    name = order[0]
    amount = int(order[1])
    date = order[2].replace('\n','')
    id = repo.vaccines.last_id + 1
    supp = repo.suppliers.find(name=name)[0]
    repo.vaccines.insert(DTO.Vaccine(id, date, supp.id, amount))
    logi = repo.logistics.find(id=supp.logistic)[0]
    repo.logistics.update({'count_received': (logi.count_received + amount)}, {'id': logi.id})


def updateOutput(file):
    file.write(repo.getSummary() + '\n')


def main(args):
    repo.createTables()
    parseConfig(args[1])
    orders = parseOrders(args[2])

    file = open(args[3], 'w')
    for order in orders:
        execOrder(order, file)

    file.close()


if __name__ == '__main__':
    main(sys.argv)
