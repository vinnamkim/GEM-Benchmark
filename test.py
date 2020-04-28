from gem.utils import plot_util, plot_stats

# Plot statistics of real graphs
plot_stats.plot_real_stats(
	in_file='gem/real_graphs_list_100.h5',
	out_file='realgraphProps.pdf'
)

# Plot benchmark results
methods = ['rand', 'pa', 'cn', 'aa', 'jc',
           'gf', 'lap', 'hope', 'sdne']
plot_util.plot_benchmark(methods, metric='MAP', s_sch='u')
