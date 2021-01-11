import datetime

import Repository

import DTO

repo = Repository.repo


def parseConfig(path):
    file = open(path, "r")
    lines = file.readlines()
    quantity = lines.pop(0).split(",")
    dto = [DTO.Vaccine, DTO.Supplier, DTO.Clinic, DTO.Logistic]
    dao = [repo.vaccines, repo.suppliers, repo.clinics, repo.logistics]

    for i in range(4):
        for j in range(int(quantity[i])):
            dao[i].insert(j, dto[i](lines.pop(0).split(',')))
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
    clinic = repo.clinics.find(location=city)
    repo.clinics.update(demand=clinic.demand - amount, location=city)
    # update count_sent & vaccine
    while amount > 0:
        vaccine = repo.vaccines.find_first()
        amount_v = vaccine.quantity
        if amount >= amount_v:
            repo.vaccines.delete(id=vaccine.id)
            curr = amount_v
        else:
            repo.vaccines.update(quantity=amount_v - amount, id=vaccine.id)
            curr = amount
        logi = repo.logistics.find(repo.suppliers.find(id=vaccine.supplier).logistic)
        repo.logistics.update(count_sent=logi.count_sent + curr, id=logi.id)
        amount = amount - amount_v


def receive(order):
    name = order[0]
    amount = int(order[1])
    date = datetime.strptime(order[2], '%Y-%m-%d')
    id = repo.vaccines.last_id + 1
    supp = repo.suppliers.find(name=name)
    repo.vaccines.insert(DTO.Vaccine(id, date, supp.id, amount))
    logi = repo.logistics.find(id=supp.logistic)
    repo.logistics.update(count_received=logi.count_received + amount, id=logi.id)


def updateOutput(file):
    file.writeline(repo.getSummary())


def main(args):
    parseConfig(args[1])
    orders = parseOrders(args[2])

    file = open(args[3], 'w')
    for order in orders:
        execOrder(order, file)

    file.close()
