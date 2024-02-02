import sys

class Database:
    '''

    Idea:
    {   
    '1-4':
        {
        'Website Location' : '1,10'
        'Link': https://teduh.kpkt.gov.my/project-swasta/1-4,
        'Maklumat Pemaju':
            {
            'Nama Pemaju': 'Chong Teck Quee & SON SDN. BHD',
            'Kod Pemaju': 1, ... 
            },
        'Ringkasan Projek':
            {
            'Kod Pemajuan': '1-4',
            'Status Projek (Keseluruhan)': 'Siap Dengan: CCC Penuh'
            },
        'Pembangunan Projek':
            {
                'Rumah 1':
                {
                'Jenis Rumah': 'Rumah Berkembar',
                'Bil. Tingkat': 1, ...
                },
                'Rumah 2:'
                {
                'Jenis Rumah': 'Rumah Teres',
                'Bil. Tingkat': 2, ...
                },
                ...       
            },
        'Lokasi Projek':
            {
            'Location': '3.55'N', 102.23'E',
            'Address': 'Jalan Temerloh, Kampung Temin, 27000 Jerantut, Pahang' 
            },
        },
    '2-4':
    ...
    }

    '''

    def __init__(self):
        self.project_data = {}
        self.important_title = ['Maklumat Pemaju', 'Ringkasan Projek', 'Pembangunan Projek', 'Lokasi Projek']
        # self.important_title = []
        self.title = []

    # def store_important_title(self, important_title):
    #     self.important_title = important_title

    def store_information_titles(self, information_titles):
        '''
        information_titles is a list of information
        [maklumat_pemaju_list, ringkasan_projek_list, pembangunan_projek_list, location_list]

        Title is in form of tuples of tuples, with key being the main title and values being the sub title
          eg: [Maklumat Pemaju, [Name Pemaju, Kod Pemaju, ...]], [Ringkasan Project, [...]], [Pembangunan Projek, [...]]
               , [Lokasi Projek,  [...]]
        '''
        title_temp = []

        if not information_titles:
            for title in self.important_title:
                title_temp.append([title, []])

        for index, info_title in enumerate(information_titles):
            title_temp.append([self.important_title[index], info_title])

        self.title = title_temp.copy()

    def add_project(self, project_title, link, data, website_location):
        '''
        add the project in the dict manner is stated above.

        project_id - a string
        link - url
        data - all the data in the webste, and is in the form of tuples of arrays, aligned with the title format
            eg: ([Chong Teck Quee, 1, ...], ['1-2', -, -, ...], [[Rumah Teres, ...], [Rumah Teres, ...], ...], ['123N, 111W', ...])

        '''
        self.project_data[project_title] = {}
        self.project_data[project_title]['Website Location'] = website_location
        self.project_data[project_title]['Link'] = link

        for section in range(len(self.important_title)):
            self.project_data[project_title][self.title[section][0]] = {}
            for index in range(len(self.title[section][1])):
                if not data[section]:
                    # self.project_data[project_title][self.title[section][0]][self.title[section][1][index]] = "-"
                    continue
                if isinstance(data[section][0], (list, tuple)):
                    # This is usually for the "Pembangunan Projek section, where there are more than a row to scrap."
                    for i in range(len(data[section])):
                        self.project_data[project_title][self.title[section][0]][f'{i+1}'] = {}
                        for indexx in range(len(data[section][i])):
                            self.project_data[project_title][self.title[section][0]][f'{i+1}'][self.title[section][1][indexx]] = data[section][i][indexx]
                    break               
                self.project_data[project_title][self.title[section][0]][self.title[section][1][index]] = data[section][index]

        print(f"Memero Usage of dict: {sys.getsizeof(self.project_data)}")

    def get_project_data(self):
        # print("Project information: \n")       
        return self.project_data
    
    def empty_data(self):
        self.project_data = {}

if __name__ == "__main__":
    d = Database()