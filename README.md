# About this project

![](example.gif)

This code simulates a 2D box full of elastically colliding spheres. Their parameters, such as mass, radius, initial position and velocity, are randomly generated (with certain constrains), but can be also be changed individually. By default, each block is colored according to its kinetic energy given by $E_\text{k} = m ||\mathbf{v} ||^2 \ / \ 2$.

The following settings in the `config.yaml` file can be adjusted:

| variable         | role                                                    |
| ---------------- | ------------------------------------------------------- |
| `canvas_size`    | canvas dimensions                                       |
| `n_blocks`       | number of randomly generated blocks                     |
| `mass_limits`    | min and max mass of a randomly generated block          |
| `radius_limits`  | min and max radius of a randomly generated block        |
| `velocity_limit` | max 1D velocity component of a randomly generated block |
| `frames`         | number of frames rendered                               |
| `fps`            | framerate of the exported video                         |
| `dpi`            | resolution of the exported video                        |

# How it works

## Block-block collisions

It is useful to declare $\mathbf{\Delta x}:= \mathbf{x}_1-\mathbf{x}_2, \ \mathbf{\Delta v}:= \mathbf{v}_1-\mathbf{v}_2$ and $\mathbf{\widehat{\Delta x}}:= \mathbf{\Delta x} \ / \ ||\mathbf{\Delta x}||$ (which is just the unit vector along $\mathbf{\Delta x}$). 

### Detection

With block radii $r_1$ and $r_2$ their overlap can be defined as $o := r_1 \ + r_2 \ - \ ||\mathbf{\Delta x}||$. Collision happens when  $o > 0$.


### Procedure

[Wikipedia provides the following solutions](https://en.wikipedia.org/wiki/Elastic_collision#Two-dimensional_collision_with_two_moving_objects) to an arbitrary 2D elastic collision:

$$\begin{align}
\mathbf{v}'_1 &= \mathbf{v}_1-\frac{2 m_2}{m_1+m_2} \ \frac{\langle \mathbf{v}_1-\mathbf{v}_2, \ \mathbf{x}_1-\mathbf{x}_2\rangle}{||\mathbf{x}_1-\mathbf{x}_2||^2} \ (\mathbf{x}_1-\mathbf{x}_2),
\\
\mathbf{v}'_2 &= \mathbf{v}_2-\frac{2 m_1}{m_1+m_2} \ \frac{\langle \mathbf{v}_2-\mathbf{v}_1, \ \mathbf{x}_2-\mathbf{x}_1\rangle}{||\mathbf{x}_2-\mathbf{x}_1||^2} \ (\mathbf{x}_2-\mathbf{x}_1)
\end{align}
$$

These equations are presented in a rather redundant form, with the results of many vector operations just differing by sign. Using previously defined variables these can be written compactly as

$$\begin{align}
\mathbf{v}'_1 &= \mathbf{v}_1 - m_2 \ c, 
\\
\mathbf{v}'_2 &= \mathbf{v}_2 + m_1 \ c,
\end{align}
$$

where the common factor $c = 2 \ \mathbf{\widehat{\Delta x}} \ \langle \mathbf{\Delta v}, \ \mathbf{\widehat{\Delta x}} \rangle \ / \ (m_1+m_2)$ only needs to be calculated once.

### Preventing stuck blocks

After the collision, to prevent block sticking together for multiple frames, their positions are adjusted so they are barely touching. Each block is moved by half of their overlap alongside the unit vector joining their centres:

$$\begin{align}
\mathbf{x}'_1 &= \mathbf{x}_1 + o \ ||\mathbf{\Delta x}|| \ / \ 2, 
\\
\mathbf{x}'_2 &= \mathbf{x}_2 - o \ ||\mathbf{\Delta x}|| \ / \ 2.
\end{align}
$$


## Block-wall collisions

### Detection

Procedure is repeated for both components of the position vector $\mathbf{x} = (x_x, \ x_y)$. For the general $i$-th component the overlap is $o := |x_i| \ + \ r - \text{box size}$. Again, collision happens when  $o > 0$.

### Procedure

In an elastic collision against the wall, the appropriate velocity component is simply negated:

$$\begin{equation}
v'_i = - \ v_i.
\end{equation}
$$

### Preventing stuck blocks

To avoid hard-coding multiple scenarios, $\text{sign}$ function can be used to always apply the correction in the opposite direction to the current (overly positive or negative) position.

$$\begin{equation}
x'_i = x_i \ - \ o \ \text{sign}(x_i) 
\end{equation}
$$
