from numpy import arctan, array, random
from scipy.stats import linregress
import matplotlib.pyplot as plt
import PySimpleGUI as sg

layout = [
    [sg.Text('Heterozygote Advantage Simulation', justification='center', font=("Arial", 24))],    
    [sg.Text('Spencer Churchill 9/21/2019')],
    [sg.Frame('Population Features',[[
        sg.Text("Genes"),
        sg.Slider(range=(1, 26), orientation='v', size=(5, 20), default_value=3),
        sg.Text("Birth rate"),
        sg.Slider(range=(1, 10), orientation='v', size=(5, 20), default_value=5),
        sg.Text("Generations"),
        sg.Slider(range=(1, 100), orientation='v', size=(5, 20), default_value=15)
        ]], relief=sg.RELIEF_SUNKEN)],
    [sg.Text("Iterations: "),
    sg.Slider(range=(1, 100), orientation='h', size=(34, 20), default_value=10)],
    [sg.Frame(layout=[
    [sg.Checkbox('Verbose output', size=(15, 1))]], title='Options',title_color='red', relief=sg.RELIEF_SUNKEN)],
    [sg.ProgressBar(100, orientation='h', size=(38, 15), key="progbar"), sg.Text("", size=(4, 1), key="progbartxt")],

    [sg.Submit(button_text="Simulate"), sg.Cancel(button_text="Exit")],
    # [sg.Canvas(size=(4, 3), key='canvas')], #### 1
]

window = sg.Window('Heterozygote Advantage', layout, default_element_size=(50, 1), finalize=True, grab_anywhere=False)

# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg #### 2
# from matplotlib.figure import Figure
# def draw_figure(plt, loc=(0, 0)):
#     figure_canvas_agg = FigureCanvasTkAgg(plt.gcf(), window["canvas"].TKCanvas)
#     figure_canvas_agg.draw()
#     figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
#     return figure_canvas_agg

def simulate(gene_count, rate, gens, num_loops, v):

    # initialize genes
    genes = []
    for gene in range(gene_count):
        allele_1 = chr(gene + 65) # begin with capital A
        allele_2 = chr(gene + 97) # then lower case a
        genes.append(allele_1 + allele_2) # Aa

    sim_info = []
    prog_num = 0
    for itera in range(num_loops):

        for simulation in range(11):

            prob = simulation/10

            gen_info = [] # include info of every generation
            info = [0, 0, 0, 0, 0] # [population, homozygous, heterozygous, death, catastrophic event]

            for gen in range(gens):

                info = [0, 0, 0, info[3], 0]

                if gen == 0:
                    # people = [genes, generation, death probability]
                    people = [[genes, 1, 0], [genes, 1, 0]] # create an inital population of 2 people
                    against = [] # determine natural selection against alleles

                for gene in genes:

                    for i, select in enumerate(against):
                        select[2] = int(select[2]) - 1
                        if select[2] == '0':
                            against.pop(i)

                    if random.random() > 1 - prob: # 1-n chance of natural selection
                        # against = [gene, how much against, number of generations]
                        val = random.random()
                        if val >= .7:
                            info[4] += 1
                        if random.randint(2) == 0:
                            against.append(array([gene[0], val, random.randint(5)], dtype=str))
                        else:
                            against.append(array([gene[1], val, random.randint(5)], dtype=str))

                # check alleles and increase chances of death when matched
                for i, person in enumerate(people):
                    person[1] += 1 # increase generation by 1
                    mort_age = 0.354 * arctan(person[1] - 3.5) + .44 # death probability from age

                    mort_nature = 0
                    for pheno in person[0]:
                        for anti in against:
                            if ord(pheno[0]) >= 97 and ord(pheno[1]) >= 97: # if gene is monozygous recessive
                                if anti[0] in pheno:
                                    mort_nature += float(anti[1]) # add anti values to death probability

                            elif ord(pheno[0]) < 97 and ord(pheno[1]) < 97: # if gene is monozygous dominant
                                if anti[0] in pheno:
                                    mort_nature += float(anti[1])

                            elif ord(pheno[0]) < ord(pheno[1]): #Aa
                                if pheno[0] == anti[0]:
                                    mort_nature += float(anti[1])

                            elif ord(pheno[1]) < ord(pheno[0]): #aA
                                if pheno[1] == anti[0]:
                                    mort_nature += float(anti[1])

                    person[2] = (1/gene_count) * mort_nature + (1) * mort_age # ratio death factors

                    if person[2] > random.random() and gen != 0: #don't kill Adam and Eve immediately
                        # print("Death probability:", person[2])
                        people.pop(i) # person killed by Darwin
                        info[3] += 1

                #birth loop
                for i in range(0, round(len(people)/2), 2):
                    for j in range(rate): # each couple has {rate} children
                        select_genes = []
                        for k in range(len(genes)):
                            allele_1 = people[i][0][k] # Aa
                            allele_2 = people[i+1][0][k] # Aa
                            punnett = []
                            punnett.append(allele_1[0] + allele_2[0]) # AA
                            punnett.append(allele_1[0] + allele_2[1]) # Aa
                            punnett.append(allele_1[1] + allele_2[0]) # aA
                            punnett.append(allele_1[1] + allele_2[1]) # aa
                            select_genes.append(random.choice(punnett)) # simulate punnett probability

                        people.append([select_genes, 1, 0]) # IT'S A BABY!!!

                info[0] = len(people) # record population of people

                # calculate heterozygous/ homozygous distributions
                total_genes = []
                for person in people: # print gene distribution
                    for gene in person[0]:
                        if ord(gene[0]) > ord(gene[1]): # check if heterozygous
                            a = gene[1]
                            b = gene[0]
                            gene = a + b # combine aA with Aa
                        total_genes.append(gene)

                for gene in total_genes:
                    if gene[0] == gene[1]:
                        info[1] += 1 # increase homozygous count
                    else:
                        info[2] += 1 # heterozygous

                gen_info.append(info)

                prog_num += 1
                progprob = 100*prog_num/(num_loops*11*gens)
                window["progbar"].UpdateBar(progprob)
                window["progbartxt"].Update(str(round(progprob))+'%')

            if len(people) == 0:
                window["progbartxt"].Update("Error")
                return
            else:
                sim_info.append(gen_info)

    if v == True:
        x = []
        y = []
        for probability, ratio in enumerate(sim_info):
            x.append(10*(probability % 11))
            y.append([100*ratio[-1][2]/(ratio[-1][1] + ratio[-1][2])])
            
        plt.scatter(x, y)
        plt.xlabel("Probability of Natural Selection (%)")
        plt.ylabel("Percent Heterozygous (%)")
        plt.title("Heterozygous Genes per Natural Selection")
        plt.show()

    #### 5) Statistically verify the trend

    # average all the values in the scatterplot
    t = []
    for i in range(11):
        t.append([])

    for i, data in enumerate(sim_info):
        t[i % 11] += [100*data[-1][2]/(data[-1][1] + data[-1][2])]

    avgs = []
    for avg in t:
        avgs.append(sum(avg)/len(avg))

    return avgs


def plot(y):
    x = range(0, 101, 10)
    bl = linregress(x, y)
    plt.title("Correlation of Averaged Scatter Plot")
    l1, = plt.plot(x, bl[0] * x + bl[1], label="Averaged Scatter Plot")
    l2, = plt.plot(x, y, label="Correlation = {}".format(bl[2]))
    plt.legend([l1, l2], ["Correlation = {}".format(round(bl[2], 1)), "Averaged Scatter Plot"])
    plt.xlabel("Probability of Natural Selection (%)")
    plt.ylabel("Percent Heterozygous (%)")
    # draw_figure(plt) #### 3
    plt.show()


while True:
    event, values = window.Read()
    if event == "Exit":
        break

    try:
        vars = simulate(int(values[0]), int(values[1]), int(values[2]), int(values[3]), values[4])
        plot(vars)
    except:
        window["progbartxt"].Update("Error")