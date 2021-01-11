from datetime import datetime
import sys
import Repository
import DTO

repo = Repository.repo


def parseConfig(path):
    file = open(path, "r")
    lines = file.readlines()
    quantity = lines.pop(0).replace('\n', '').split(",")
    dto = [DTO.Vaccine, DTO.Supplier, DTO.Clinic, DTO.Logistic]
    dao = [repo.vaccines, repo.suppliers, repo.clinics, repo.logistics]

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
        orders.append(line.split(','))
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
    # update count_sent & vaccine
    while amount > 0:
        vaccine = repo.firstVaccine()[0]
        amount_v = vaccine.quantity
        if amount >= amount_v:
            repo.vaccines.delete(id=vaccine.id)
            curr = amount_v
        else:
            repo.vaccines.update({'quantity': amount_v - amount}, {'id': vaccine.id})
            curr = amount
        logi = repo.logistics.find(id = repo.suppliers.find(id=vaccine.supplier)[0].logistic)[0]
        repo.logistics.update({'count_sent': (logi.count_sent + curr)}, {'id': logi.id})
        amount = amount - amount_v


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
    print("summary = "+repo.getSummary())
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
