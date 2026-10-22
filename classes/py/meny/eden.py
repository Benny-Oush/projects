def frequency_report(values):
    dic = {}
    for value in values:
        if value not in dic:
            dic[value] = 1
            continue
        dic[value] += 1
    return (dic, [(k, v) for k, v in sorted(dic.items(), key=lambda item: item[1], reverse=True) if v > 1], [k for k, v in dic.items() if v == 1])

def group_students(rows):
    result = {}
    for pair in rows:
        if pair[0] not in result:
            result[pair[0]] = [pair[1]]
            continue
        result[pair[0]].append(pair[1])
    for k in result.keys():
        result[k] = list(set(result[k]))
    return result

def group_sizes(groups):
    return [(k, len(v)) for k, v in groups.items()]


