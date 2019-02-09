

def choose_chinese_character(goal):
    for each in goal:
        x = 80
        status = True
        while status:
            s = bytes(each["title"], 'utf8')[:x]
            try:
                sss = s.decode('utf8')
            except:
                x -= 1
            else:
                status = False
        each["title"] = sss
    return


class Page():
    def __init__(self, page_num, total_count, per_page=3, max_page=3):
        """

        :param page_num:
        :param total_count:
        :param per_page:
        :param max_page:
        """
        total_page, m = divmod(total_count,per_page)
        if m:
            total_page += 1
        self.total_page = total_page

        try:
            page_num = int(page_num)
            if page_num > total_page:
                page_num = total_page
        except Exception as e:
            page_num = 1
        self.page_num = page_num

        self.data_start = (page_num - 1) * per_page
        self.data_end = page_num * per_page

        # 一次展示多少頁碼
        if self.total_page < max_page:  # 設定當頁面總數小於max_page時，展示的頁數
            max_page = self.total_page  # 直接設定max_page，就絕不會超出total_page了
        self.max_page = max_page

        half_max_page = self.max_page // 2  # 地板除
        page_start = page_num - half_max_page
        page_end = page_num + half_max_page
        # 如果當前頁面 減一半 比1還小
        if page_start <= 1:
            page_start = 1
            page_end = self.max_page
        # 如果當前頁面 加一半 比總頁碼還大
        if page_end >= total_page:
            page_end = total_page
            page_start = total_page - self.max_page + 1
        self.page_start = page_start
        self.page_end = page_end

    @property
    def start(self):
        return self.data_start

    @property
    def end(self):
        return self.data_end

    def page_html(self):
        html_str_list = []
        if self.page_num > 1:
            html_str_list.append('<button value="'+str(self.page_num-1)+'">上一頁</button>')
        if self.page_start > 1:
            html_str_list.append('<button>1</button>')
            html_str_list.append('<span>&nbsp;...&nbsp;</span>')
        for i in range(self.page_start, self.page_end + 1):
            # 如果是當前頁就disabled="true"
            if i == self.page_num:
                tmp = '<button disabled="true">'+str(i)+'</button>'
            else:
                tmp = '<button>'+str(i)+'</button>'
            html_str_list.append(tmp)
        if self.page_end < self.total_page:
            html_str_list.append('<span>&nbsp;...&nbsp;</span>')
            html_str_list.append('<button>'+str(self.total_page)+'</button>')
        if self.page_num < self.total_page:
            html_str_list.append('<button value="'+str(self.page_num+1)+'">下一頁</button>')

        page_html = "".join(html_str_list)
        return page_html
